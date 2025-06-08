import requests
import logging
import os
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
WHOIS_API_KEY = os.getenv("WHOIS_API_KEY")
WHOIS_API_URL = "https://www.whoisxmlapi.com/api/v1"

# Heuristic settings
BLACKLISTED_DOMAINS = ["phishing-example.com", "suspicious-site.net"]
SUSPICIOUS_KEYWORDS = ["login", "update", "secure", "verify", "bank", "password", "account"]
DOMAIN_AGE_THRESHOLD = 30  # Days

def check_phishing_rules(url):
    """Perform heuristic-based phishing detection using domain info and URL patterns."""
    try:
        hostname = extract_hostname(url)
        if not hostname:
            return {"result": "unknown", "reason": "Invalid hostname extracted."}

        # 1️⃣ Check suspicious keywords in URL
        if any(keyword in url.lower() for keyword in SUSPICIOUS_KEYWORDS):
            return {
                "result": "phishing",
                "reason": "Suspicious keywords detected in the URL."
            }

        # 2️⃣ Check if domain is recently registered
        domain_age = get_domain_age(hostname)
        if domain_age < DOMAIN_AGE_THRESHOLD:
            return {
                "result": "phishing",
                "reason": f"Domain is newly registered ({domain_age} days old)."
            }

        # 3️⃣ Check if domain is blacklisted
        if hostname in BLACKLISTED_DOMAINS:
            return {
                "result": "phishing",
                "reason": "Blacklisted domain detected."
            }

        return {
            "result": "legitimate",
            "reason": "No suspicious indicators found."
        }

    except Exception as e:
        logging.error(f"Error in heuristic phishing detection: {str(e)}")
        return {
            "result": "unknown",
            "reason": "Error during heuristic analysis."
        }

def extract_hostname(url):
    """Extract the hostname from a URL."""
    try:
        parsed_url = urlparse(url)
        return parsed_url.hostname
    except Exception as e:
        logging.error(f"Failed to extract hostname: {str(e)}")
        return None

def get_domain_age(hostname):
    """Return the age of a domain in days using WHOIS lookup."""
    try:
        if not WHOIS_API_KEY:
            logging.warning("WHOIS API key is missing. Skipping domain age check.")
            return float("inf")

        response = requests.get(
            f"{WHOIS_API_URL}?domain={hostname}&apiKey={WHOIS_API_KEY}",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if "creationDate" in data:
            creation_date = datetime.strptime(data["creationDate"], "%Y-%m-%d")
            return (datetime.now() - creation_date).days

        logging.warning(f"No creationDate found in WHOIS data for {hostname}")
        return float("inf")

    except requests.exceptions.RequestException as req_err:
        logging.error(f"WHOIS API request failed: {str(req_err)}")
        return float("inf")
    except Exception as e:
        logging.error(f"Error parsing WHOIS response: {str(e)}")
        return float("inf")
