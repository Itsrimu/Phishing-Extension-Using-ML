const WHOIS_API_URL = "https://api.whoisxmlapi.com/v1"; // Replace with real API URL
let WHOIS_API_KEY = "YOUR_API_KEY"; // Will be dynamically updated if needed

const BLACKLISTED_DOMAINS = ["phishing-example.com", "suspicious-site.net"];
const SUSPICIOUS_KEYWORDS = ["login", "update", "secure", "verify", "bank"];
const DOMAIN_AGE_THRESHOLD = 30; // days

/**
 * Checks URL for phishing signs.
 * @param {string} url
 * @returns {Promise<{ result: string, reason: string }>}
 */
export async function checkPhishingRules(url) {
  try {
    const { hostname } = new URL(url);
    const domain = hostname.toLowerCase();

    if (SUSPICIOUS_KEYWORDS.some(keyword => url.toLowerCase().includes(keyword))) {
      return { result: "phishing", reason: "Suspicious keyword found in URL" };
    }

    if (BLACKLISTED_DOMAINS.includes(domain)) {
      return { result: "phishing", reason: "Domain found in blacklist" };
    }

    const age = await getDomainAge(domain);
    if (age < DOMAIN_AGE_THRESHOLD) {
      return { result: "phishing", reason: `Domain is very new (Age: ${age} days)` };
    }

    return { result: "legitimate", reason: "No phishing indicators found" };
  } catch (error) {
    console.error("Phishing check error:", error);
    return { result: "unknown", reason: "Error occurred during analysis" };
  }
}

/**
 * Gets domain age in days.
 * @param {string} hostname
 * @returns {Promise<number>}
 */
async function getDomainAge(hostname) {
  try {
    const storage = await chrome.storage.local.get(["apiKey"]);
    WHOIS_API_KEY = storage.apiKey || WHOIS_API_KEY;

    const response = await fetch(`${WHOIS_API_URL}?domain=${hostname}&apiKey=${WHOIS_API_KEY}`);
    const data = await response.json();

    if (!data || !data.creationDate) return Number.MAX_SAFE_INTEGER;

    const createdDate = new Date(data.creationDate);
    const diffMs = Date.now() - createdDate.getTime();
    return Math.floor(diffMs / (1000 * 60 * 60 * 24)); // Days
  } catch (err) {
    console.error("WHOIS lookup failed:", err);
    return Number.MAX_SAFE_INTEGER;
  }
}
