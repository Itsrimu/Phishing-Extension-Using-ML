# File: feature.py

import re
import socket
import ssl
import ipaddress
import tldextract
from urllib.parse import urlparse, unquote
import datetime

SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'secure', 'account', 'update', 'signin', 'banking',
    'confirm', 'validate', 'reset', 'submit'
]

SUSPICIOUS_TLDS = {'tk', 'ml', 'ga', 'cf', 'gq'}

URL_SHORTENERS = {'bit.ly', 'goo.gl', 't.co', 'tinyurl.com', 'is.gd', 'ow.ly'}

FEATURE_NAMES = [
    "url_length", "domain_length", "path_length", "query_length", "num_dots", "num_hyphens",
    "num_underscores", "num_slashes", "num_digits", "num_letters", "ratio_digits", "ratio_letters",
    "has_https", "count_https_token", "has_ip", "has_at_symbol", "has_port", "has_query",
    "has_equals", "has_double_slash", "num_subdomains", "suspicious_keywords_count",
    "has_suspicious_keyword", "tld_length", "is_tld_suspicious", "is_trusted_domain",
    "domain_is_short", "is_https_and_trusted"
]

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

def validate_ssl(domain):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(2)
            s.connect((domain, 443))
            cert = s.getpeercert()
            expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            issue_date = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
            issuer = cert['issuer'][0][0][1]
            cn = cert['subject'][0][0][1]
            return {
                "valid_ssl_cert": expire_date > datetime.datetime.utcnow(),
                "ssl_cert_age_days": (datetime.datetime.utcnow() - issue_date).days,
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

def is_ip(domain: str) -> bool:
    return bool(re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", domain))

def count_https_token(url: str) -> int:
    return url.count('https')

def extract_url_features(url: str, skip_ssl: bool = False) -> dict:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Invalid URL")

    url = url.strip().lower()

    # Parse URL safely
    try:
        parsed = urlparse(url if url.startswith(('http://', 'https://')) else f"http://{url}")
        domain = parsed.netloc
        path = parsed.path
        query = parsed.query
        full = f"{domain}{path}?{query}"
    except Exception as e:
        # Return zeros for all features if parsing fails
        return {name: 0 for name in FEATURE_NAMES}

    suspicious_keywords = [
        "secure", "account", "update", "login", "signin", "banking", "confirm", "password",
        "ebay", "paypal", "dropbox", "admin", "submit", "wp-admin", "webscr", "verify"
    ]
    trusted_keywords = [
        "gov", ".gov", ".edu", "who.int", "nasa.gov", "india.gov.in", "europa.eu"
    ]

    features = {
        "url_length": len(url),
        "domain_length": len(domain),
        "path_length": len(path),
        "query_length": len(query),
        "num_dots": full.count('.'),
        "num_hyphens": full.count('-'),
        "num_underscores": full.count('_'),
        "num_slashes": full.count('/'),
        "num_digits": sum(c.isdigit() for c in full),
        "num_letters": sum(c.isalpha() for c in full),
        "ratio_digits": sum(c.isdigit() for c in full) / len(full) if full else 0,
        "ratio_letters": sum(c.isalpha() for c in full) / len(full) if full else 0,
        "has_https": int(url.startswith("https")),
        "count_https_token": count_https_token(url),
        "has_ip": int(is_ip(domain)),
        "has_at_symbol": int("@" in url),
        "has_port": int(":" in domain and not domain.endswith(':')),
        "has_query": int(bool(query)),
        "has_equals": int("=" in query),
        "has_double_slash": int('//' in url[8:]),  # beyond protocol
        "num_subdomains": domain.count('.') - 1 if domain else 0,
        "suspicious_keywords_count": sum(word in url for word in suspicious_keywords),
        "has_suspicious_keyword": int(any(word in url for word in suspicious_keywords)),
        "tld_length": len(domain.split('.')[-1]) if '.' in domain else 0,
        "is_tld_suspicious": int(domain.endswith('.xyz') or domain.endswith('.tk') or domain.endswith('.cf')),
        "is_trusted_domain": int(any(trusted in domain for trusted in trusted_keywords)),
        "domain_is_short": int(len(domain) < 15),
        "is_https_and_trusted": int(url.startswith("https") and any(t in domain for t in trusted_keywords)),
    }

    # Ensure all features are present and numeric
    for name in FEATURE_NAMES:
        if name not in features:
            features[name] = 0

    # SSL features
    ssl_feats = validate_ssl(domain) if parsed.scheme == 'https' and not skip_ssl else {
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
        "https_enabled": parsed.scheme == 'https',
        "has_suspicious_keywords": any(word in unquote(url).lower() for word in SUSPICIOUS_KEYWORDS),
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

    # Aliases expected by the ML model
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

    # Simple flag reason logic
    if feats["has_suspicious_keywords"] and feats["subdomain_count"] > 2:
        feats["flag_reason"] = "Suspicious keywords and many subdomains"
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
