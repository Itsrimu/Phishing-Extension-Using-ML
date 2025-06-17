(async () => {
  const API_BASE_URL = "http://127.0.0.1:5000/api";
  const reportedUrls = new Set();

  // Show a top banner alert
  function showBanner(message, isPhishing) {
    if (document.getElementById("phishing-banner")) return;

    const banner = document.createElement("div");
    banner.id = "phishing-banner";
    Object.assign(banner.style, {
      position: "fixed",
      top: "0",
      left: "50%",
      transform: "translateX(-50%)",
      width: "60%",
      padding: "12px 20px",
      fontSize: "15px",
      fontWeight: "bold",
      color: "#fff",
      backgroundColor: isPhishing ? "#d32f2f" : "#388e3c",
      fontFamily: "Arial, sans-serif",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      zIndex: "9999",
      borderRadius: "0 0 8px 8px",
      boxShadow: "0 2px 6px rgba(0, 0, 0, 0.2)",
    });

    const text = document.createElement("span");
    text.textContent = message;

    const closeBtn = document.createElement("span");
    closeBtn.textContent = "✖";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.marginLeft = "15px";
    closeBtn.setAttribute("aria-label", "Close warning");
    closeBtn.onclick = () => banner.remove();

    banner.appendChild(text);
    banner.appendChild(closeBtn);
    document.body.prepend(banner);

    // Auto-remove after 10 seconds
    setTimeout(() => banner.remove(), 10000);
  }

  // Run phishing check on the current page
  async function checkCurrentPage() {
    const url = window.location.href;
    if (!/^https?:\/\//.test(url)) return;

    try {
      const response = await fetch(`${API_BASE_URL}/predict-only`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const result = await response.json();

      // Accept both {verdict: "..."} and {analysis_result: "..."} 
      const verdict = result.verdict || result.analysis_result;
      if (verdict && verdict.toLowerCase() === "phishing") {
        showBanner(`Phishing Detected!`, true);
      }
    } catch (err) {
      showBanner("Unable to contact phishing detection service.", false);
    }
  }

  // Highlight links flagged as phishing
  // Removed batch call because backend lacks /predict-batch
  async function highlightLinks() {
    // Could implement single requests with debounce if desired
  }

  // Expand shortened URLs (unchanged, uses external API)
  async function expandShortLinks() {
    const selectors = [
      "a[href*='bit.ly']",
      "a[href*='tinyurl']",
      "a[href*='t.co']",
      "a[href*='ow.ly']",
      "a[href*='goo.gl']",
      "a[href*='buff.ly']"
    ];
    const links = document.querySelectorAll(selectors.join(", "));

    for (const link of links) {
      const shortUrl = link.href;

      try {
        const response = await fetch(`https://api.unshorten.me/?url=${encodeURIComponent(shortUrl)}`);
        if (!response.ok) continue;

        const data = await response.json();
        if (data?.unshortened_url) {
          link.title = `🔗 Full URL: ${data.unshortened_url}`;
        }
      } catch {
        // Silent fail, skip link
      }
    }
  }

  // Context-menu phishing report
  function setupRightClickReporting() {
    document.addEventListener("contextmenu", (event) => {
      const link = event.target.closest("a[href]");
      if (!link || !/^https?:\/\//.test(link.href)) return;

      const url = link.href;
      if (reportedUrls.has(url)) return;

      setTimeout(() => {
        if (confirm(`Report this URL as phishing?\n\n${url}`)) {
          reportedUrls.add(url);

          fetch(`${API_BASE_URL}/feedback/report`, { // <-- changed endpoint
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url, reason: "Manual user report" }),
          })
            .then(res => {
              if (!res.ok) throw new Error("Report failed.");
              return res.json();
            })
            .then(() => alert("Phishing report submitted. Thank you!"))
            .catch(() => alert("Failed to submit report."));
        }
      }, 50);
    });
  }

  // Tooltip for link predictions
  (function () {
    let tooltip = null;
    let lastUrl = "";
    let verdictCache = {};

    function createTooltip() {
      tooltip = document.createElement("div");
      tooltip.style.position = "fixed";
      tooltip.style.zIndex = "99999";
      tooltip.style.padding = "6px 12px";
      tooltip.style.borderRadius = "6px";
      tooltip.style.fontSize = "13px";
      tooltip.style.fontWeight = "bold";
      tooltip.style.pointerEvents = "none";
      tooltip.style.boxShadow = "0 2px 8px rgba(0,0,0,0.15)";
      tooltip.style.display = "none";
      document.body.appendChild(tooltip);
    }

    function showTooltip(text, color, x, y) {
      if (!tooltip) createTooltip();
      tooltip.textContent = text;
      tooltip.style.background = color;
      tooltip.style.color = "#fff";
      tooltip.style.left = x + 15 + "px";
      tooltip.style.top = y + 15 + "px";
      tooltip.style.display = "block";
    }

    function hideTooltip() {
      if (tooltip) tooltip.style.display = "none";
    }

    document.addEventListener("mouseover", async (e) => {
      const link = e.target.closest("a[href]");
      if (!link) return hideTooltip();

      const url = link.href;
      lastUrl = url;

      // If verdict is cached, use it
      if (verdictCache[url]) {
        showTooltip(verdictCache[url].text, verdictCache[url].color, e.clientX, e.clientY);
        return;
      }

      showTooltip("Checking...", "#888", e.clientX, e.clientY);

      try {
        const res = await fetch(`${API_BASE_URL}/predict-only`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url }),
        });
        const data = await res.json();
        const verdict = (data.verdict || data.analysis_result || "").toLowerCase();
        let text, color;
        if (verdict === "phishing") {
          text = "Unsafe (Phishing)";
          color = "#d32f2f";
        } else if (verdict === "legitimate") {
          text = "Safe";
          color = "#388e3c";
        } else {
          text = "Unknown";
          color = "#888";
        }
        verdictCache[url] = { text, color };
        // Only show if still hovering the same link
        if (lastUrl === url) showTooltip(text, color, e.clientX, e.clientY);
      } catch {
        showTooltip("Error checking", "#888", e.clientX, e.clientY);
      }
    });

    document.addEventListener("mousemove", (e) => {
      if (tooltip && tooltip.style.display === "block") {
        tooltip.style.left = e.clientX + 15 + "px";
        tooltip.style.top = e.clientY + 15 + "px";
      }
    });

    document.addEventListener("mouseout", (e) => {
      if (e.target.closest("a[href]")) hideTooltip();
    });
  })();

  let autoDetectEnabled = false;

  // Listen for changes to autoDetect setting
  chrome.storage.local.get(["autoDetect"], (data) => {
    autoDetectEnabled = !!data.autoDetect;
    if (autoDetectEnabled) {
      checkCurrentPage(); // or whatever auto-detection should do
    }
  });

  chrome.storage.onChanged.addListener((changes, area) => {
    if (area === "local" && changes.autoDetect) {
      autoDetectEnabled = changes.autoDetect.newValue;
      if (autoDetectEnabled) {
        checkCurrentPage();
      } else {
        // Optionally, remove banners/tooltips if disabling
      }
    }
  });

  // Run all
  await checkCurrentPage();
  // highlightLinks() is disabled due to missing backend endpoint
  await expandShortLinks();
  setupRightClickReporting();
})();
