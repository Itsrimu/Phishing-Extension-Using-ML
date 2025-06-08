const API_BASE = "http://127.0.0.1:5000/api";
let lastCheckedUrl = "";

// Auto-detect phishing after navigation
chrome.webNavigation.onCompleted.addListener(
  async ({ url }) => {
    if (!isValidHttpUrl(url) || isChromeInternal(url)) return;

    const autoDetect = await getAutoDetectionEnabled();
    if (autoDetect) checkPhishing(url);
  },
  { url: [{ schemes: ["http", "https"] }] }
);

// Message listener from popup or content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  const { action, url, feedback, reason } = request;

  if (!isValidHttpUrl(url)) return;

  switch (action) {
    case "checkUrl":
    case "hoverCheck":
      checkPhishing(url);
      break;
    case "storeFeedback":
      submitFeedback(url, feedback);
      break;
    case "reportPhishing":
      submitReport(url, reason);
      break;
  }

  return true; // Keep async message channel open
});

// Validate HTTP/HTTPS URLs
function isValidHttpUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
}

// Exclude chrome:// and extension:// URLs
function isChromeInternal(url) {
  return url.startsWith("chrome://") || url.startsWith("chrome-extension://");
}

// Get user auto-detect setting from storage
function getAutoDetectionEnabled() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["autoDetect"], (result) => {
      resolve(result.autoDetect === true);
    });
  });
}

// Check URL for phishing (calls /predict-only)
function checkPhishing(url) {
  if (url === lastCheckedUrl) return;
  lastCheckedUrl = url;

  fetchWithTimeout(`${API_BASE}/predict-only`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  })
    .then((data) => {
      // Accept both {verdict: "..."} and {analysis_result: "..."} 
      const verdict = data.verdict || data.analysis_result;
      if (verdict && verdict.toLowerCase() === "phishing") {
        notifyUser(url, "Phishing Alert", "This site may be unsafe.");
      }
    })
    .catch(() => {
      // Optional: console.error("Phishing check failed:", err);
    });
}

// Show Chrome desktop notification
function notifyUser(url, title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icons/icon128.png",
    title,
    message: `${message}\n\nURL: ${url}`,
    priority: 2,
    requireInteraction: false,
  });
}

// Submit feedback to /feedback
function submitFeedback(url, feedback) {
  fetchWithTimeout(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, feedback }),
  }).catch(() => {});
}

// Submit phishing report to /feedback/report
function submitReport(url, reason = "User reported phishing") {
  fetchWithTimeout(`${API_BASE}/feedback/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, reason }),
  })
    .then(() => {
      notifyUser(url, "Report Submitted", "Thanks for reporting this site.");
    })
    .catch(() => {});
}

// Optionally: Periodically fetch reported URLs for retraining
function fetchReportedForRetraining() {
  fetchWithTimeout(`${API_BASE}/feedback/reported_phishing`)
    .then((data) => {
      // Process retraining data if needed
    })
    .catch(() => {});
}

// Generalized fetch helper with abort timeout
function fetchWithTimeout(url, options, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);

    fetch(url, { ...options, signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        clearTimeout(timer);
        resolve(data);
      })
      .catch((err) => {
        clearTimeout(timer);
        reject(err);
      });
  });
}

// Optionally fetch retraining samples daily
setInterval(fetchReportedForRetraining, 24 * 60 * 60 * 1000);
