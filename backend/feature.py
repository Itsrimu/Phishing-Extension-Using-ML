# File: feature.py

import re
import socket
import ssl
import whois
import ipaddress
import datetime
import tldextract
from urllib.parse import urlparse, unquote

# Suspicious terms often used in phishing
SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'secure', 'account', 'update', 'signin', 'banking',
    'confirm', 'validate', 'reset', 'submit'
]

# Common suspicious TLDs
SUSPICIOUS_TLDS = {'tk', 'ml', 'ga', 'cf', 'gq'}

# Common URL shorteners
URL_SHORTENERS = {'bit.ly', 'goo.gl', 't.co', 'tinyurl.com', 'is.gd', 'ow.ly'}

def extract_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def is_ip_address(domain):
    try:
        ipaddress.ip_address(domain)
        return True
    except ValueError:
        return False

def is_private_ip(domain):
    try:
        ip = ipaddress.ip_address(domain)
        return ip.is_private
    except:
        return False

def get_domain_age(domain):
    try:
        w = whois.whois(domain)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        age = (datetime.datetime.now() - creation).days
        return age
    except:
        return -1

def validate_ssl(domain):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain, 443))
            cert = s.getpeercert()
            expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            issue_date = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            issuer = cert['issuer'][0][0][1]
            cn = cert['subject'][0][0][1]
            return {
                "valid_ssl_cert": expire_date > datetime.datetime.now(),
                "ssl_cert_age_days": (datetime.datetime.now() - issue_date).days,
                "ssl_cert_issuer": issuer,
                "ssl_matches_domain": domain in cn
            }
    except:
        return {
            "valid_ssl_cert": False,
            "ssl_cert_age_days": -1,
            "ssl_cert_issuer": "Unknown",
            "ssl_matches_domain": False
        }

def extract_url_features(url: str) -> dict:
    parsed = urlparse(url)
    domain  = extract_domain(url)
    netloc  = parsed.netloc.split('@')[-1].split(':')[0]
    is_ip   = is_ip_address(netloc)

    ssl_feats = validate_ssl(domain) if parsed.scheme == 'https' else {
        "valid_ssl_cert": False,
        "ssl_cert_age_days": -1,
        "ssl_cert_issuer": "None",
        "ssl_matches_domain": False
    }

    feats = {
        "url": url,
        "uses_ip_address": is_ip,
        "is_private_ip": is_private_ip(netloc) if is_ip else False,
        "domain": domain,
        "domain_age_days": get_domain_age(domain),
        "https_enabled": parsed.scheme == 'https',
        "has_suspicious_keywords": any(w in unquote(url).lower() for w in SUSPICIOUS_KEYWORDS),
        "url_length": len(url),
        "has_hex_encoding": bool(re.search(r'%[0-9a-fA-F]{2}', url)),
        "has_at_symbol": '@' in url,
        "has_double_slash_path": '//' in parsed.path.lstrip('/'),
        "subdomain_count": netloc.count('.') - 1,
        "tld_in_suspicious_list": domain.split('.')[-1] in SUSPICIOUS_TLDS,
        "shortened_url": domain in URL_SHORTENERS,
        "contains_port": ':' in parsed.netloc,
        "domain_in_whitelist": False,  # Placeholder
        "ai_confidence_score": -1.0,   # Placeholder
        **ssl_feats
    }

    # Add feature aliases expected by the model
    feats.update({
        "has_ip": feats["uses_ip_address"],
        "ip_is_private": feats["is_private_ip"],
        "has_suspicious_keyword": feats["has_suspicious_keywords"],
        "is_tld_suspicious": feats["tld_in_suspicious_list"],
        "count_https_token": feats["url"].count("https"),
        "has_double_slash": feats["has_double_slash_path"],
        "has_https": feats["https_enabled"],
        "domain_is_short": len(domain) <= 5,
        "ssl_valid": int(feats["valid_ssl_cert"]),
    })

    # Optional flag reason
    if feats["has_suspicious_keywords"] and feats["domain_age_days"] != -1 and feats["domain_age_days"] < 30:
        feats["flag_reason"] = "Suspicious keywords + new domain"
    elif feats["uses_ip_address"] and not feats["is_private_ip"]:
        feats["flag_reason"] = "Public IP used as domain"
    elif feats["shortened_url"]:
        feats["flag_reason"] = "Shortened URL"
    elif feats["has_at_symbol"]:
        feats["flag_reason"] = "Obfuscated with '@'"
    elif not feats["https_enabled"]:
        feats["flag_reason"] = "Not using HTTPS"
    else:
        feats["flag_reason"] = ""

    return feats
