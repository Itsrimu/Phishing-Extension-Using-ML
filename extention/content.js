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

  // Run all
  await checkCurrentPage();
  // highlightLinks() is disabled due to missing backend endpoint
  await expandShortLinks();
  setupRightClickReporting();
})();
