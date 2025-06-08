document.addEventListener("DOMContentLoaded", () => {
  const statusIndicator = document.getElementById("status-indicator");
  const phishingWarning = document.getElementById("phishing-warning");
  const feedbackButtons = document.querySelectorAll(".feedback-btn");
  const reportBtn = document.getElementById("report-btn");
  const showMoreBtn = document.getElementById("show-more-btn");
  const autoDetectCheckbox = document.getElementById("autoDetect");
  const openSettingsBtn = document.getElementById("open-settings-btn");
  const checkUrlBtn = document.getElementById("check-url-btn");

  const API_BASE_URL = "http://127.0.0.1:5000/api";
  let currentUrl = "";

  chrome.storage.local.get(["autoDetect"], (data) => {
    const enabled = data.autoDetect || false;
    autoDetectCheckbox.checked = enabled;
    statusIndicator.textContent = `Auto-Detection ${enabled ? "Enabled" : "Disabled"}`;
    if (enabled) fetchAndCheckActiveTab();
  });

  autoDetectCheckbox.addEventListener("change", () => {
    const enabled = autoDetectCheckbox.checked;
    chrome.storage.local.set({ autoDetect: enabled }, () => {
      statusIndicator.textContent = `Auto-Detection ${enabled ? "Enabled" : "Disabled"}`;
      if (enabled) fetchAndCheckActiveTab();
    });
  });

  checkUrlBtn.addEventListener("click", () => {
    if (!currentUrl) fetchAndCheckActiveTab();
    else checkUrl(currentUrl);
  });

  reportBtn.addEventListener("click", () => {
    if (!currentUrl) return;
    fetch(`${API_BASE_URL}/feedback/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: currentUrl, reason: "User suspects phishing" }),
    })
      .then((res) => res.json())
      .then((data) => {
        statusIndicator.textContent = data.status === "success"
          ? "Phishing Report Submitted!"
          : "Failed to report the site.";
      })
      .catch(() => {
        statusIndicator.textContent = "Failed to report the site.";
      });
  });

  feedbackButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const feedback = btn.dataset.feedback;
      if (!currentUrl || !feedback) return;

      fetch(`${API_BASE_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: currentUrl, feedback }),
      })
        .then((res) => res.json())
        .then((data) => {
          statusIndicator.textContent = data.feedback_updated
            ? "Feedback submitted!"
            : "Feedback submission failed.";
        })
        .catch(() => {
          statusIndicator.textContent = "Feedback submission failed.";
        });
    });
  });

  openSettingsBtn.addEventListener("click", () => {
    chrome.tabs.create({ url: chrome.runtime.getURL("settings.html") });
  });

  showMoreBtn.addEventListener("click", () => {
    if (currentUrl) {
      chrome.tabs.create({
        url: `https://www.phishcheck.ai/info?url=${encodeURIComponent(currentUrl)}`,
      });
    }
  });

  function fetchAndCheckActiveTab() {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs[0];
      if (!tab || !tab.url || !/^https?:\/\//i.test(tab.url)) {
        statusIndicator.textContent = "Invalid or unsupported tab URL.";
        phishingWarning.classList.add("hidden");
        currentUrl = "";
        return;
      }
      currentUrl = tab.url;
      checkUrl(currentUrl);
    });
  }

  function checkUrl(url) {
    statusIndicator.textContent = "Checking for phishing risks...";
    phishingWarning.classList.add("hidden");

    fetch(`${API_BASE_URL}/predict-only`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    })
      .then((res) => res.json())
      .then((data) => {
        // Accept both {verdict: "..."} and {analysis_result: "..."
        const verdict = data.verdict || data.analysis_result;
        if (verdict) {
          if (verdict.toLowerCase() === "phishing") {
            phishingWarning.classList.remove("hidden");
            statusIndicator.textContent = "Phishing Detected!"
              + (data.confidence ? ` (${data.confidence})` : "");
          } else {
            phishingWarning.classList.add("hidden");
            statusIndicator.textContent = "Legitimate Site"
              + (data.confidence ? ` (${data.confidence})` : "");
          }
        } else if (data.error) {
          statusIndicator.textContent = `Error: ${data.error}`;
        } else {
          statusIndicator.textContent = "Unexpected server response.";
        }
      })
      .catch(() => {
        statusIndicator.textContent = "Server error while checking.";
      });
  }

  fetchAndCheckActiveTab();
});
