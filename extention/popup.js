document.addEventListener("DOMContentLoaded", function () {
  const resultText = document.getElementById("result-text");
  const feedbackButtons = document.querySelectorAll(".feedback-btn");
  const reportBtn = document.getElementById("report-btn");
  const showMoreBtn = document.getElementById("show-more-btn");

  let currentUrl = "";

  // Fetch the active tab URL when popup opens
  chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    if (tabs.length === 0 || !tabs[0].url) {
      resultText.textContent = " Unable to fetch active tab URL.";
      return;
    }

    currentUrl = tabs[0].url;
    resultText.textContent = " Checking URL...";

    fetch("http://127.0.0.1:5000/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: currentUrl })
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log(" API Response:", data); // Debugging line

        if (data && data.result) {
          const verdict = data.result.toLowerCase();
          const confidence = data.confidence || "Unknown";

          resultText.textContent = verdict === "phishing"
            ? ` Phishing detected! (Confidence: ${confidence}%)`
            : ` Legitimate site (Confidence: ${confidence}%)`;
        } else {
          resultText.textContent = " Error: Invalid response from server.";
        }
      })
      .catch(error => {
        console.error(" Prediction Error:", error);
        resultText.textContent = " Server error while checking URL.";
      });
  });

  // Handle feedback submission
  feedbackButtons.forEach(button => {
    button.addEventListener("click", () => {
      const feedback = button.dataset.feedback;
      if (!currentUrl) return;

      fetch("http://127.0.0.1:5000/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: currentUrl, feedback })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          return response.json();
        })
        .then(() => {
          resultText.textContent = "Feedback submitted. Thank you!";
        })
        .catch(err => {
          console.error(" Feedback Error:", err);
          resultText.textContent = " Failed to send feedback.";
        });
    });
  });

  // Show More action
  showMoreBtn.addEventListener("click", () => {
    if (currentUrl) {
      chrome.tabs.create({
        url: `https://www.phishcheck.ai/info?url=${encodeURIComponent(currentUrl)}`
      });
    }
  });

  // Report action
  reportBtn.addEventListener("click", () => {
    if (currentUrl) {
      fetch("http://127.0.0.1:5000/api/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: currentUrl, message: "User reported phishing." })
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
          return response.json();
        })
        .then(() => {
          resultText.textContent = " Report submitted!";
        })
        .catch(err => {
          console.error(" Report Error:", err);
          resultText.textContent = " Failed to report URL.";
        });
    }
  });
});
