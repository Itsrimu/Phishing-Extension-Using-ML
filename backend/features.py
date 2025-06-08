# File: backend/features.py

import re
from urllib.parse import urlparse

FEATURE_NAMES = [
    "url_length", "domain_length", "path_length", "query_length", "num_dots", "num_hyphens",
    "num_underscores", "num_slashes", "num_digits", "num_letters", "ratio_digits", "ratio_letters",
    "has_https", "count_https_token", "has_ip", "has_at_symbol", "has_port", "has_query",
    "has_equals", "has_double_slash", "num_subdomains", "suspicious_keywords_count",
    "has_suspicious_keyword", "tld_length", "is_tld_suspicious", "is_trusted_domain",
    "domain_is_short", "is_https_and_trusted"
]

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

    return features