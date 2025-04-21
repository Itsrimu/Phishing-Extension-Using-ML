document.addEventListener("DOMContentLoaded", function () {
    const checkBtn = document.getElementById("check-btn");
    const resultDiv = document.getElementById("result");
    const currentUrlP = document.getElementById("current-url");
    const feedbackSection = document.getElementById("feedback-section");
    const feedbackButtons = document.querySelectorAll(".feedback-btn");
  
    let currentUrl = "";
    let currentRecordId = "";
  
    // Fetch the current tab URL
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      if (tabs.length > 0) {
        currentUrl = tabs[0].url;
        currentUrlP.textContent = currentUrl;
      } else {
        currentUrlP.textContent = "Unable to fetch current tab URL.";
      }
    });
  
    checkBtn.addEventListener("click", function () {
      if (!currentUrl) return;
  
      // Reset result and feedback section
      resultDiv.classList.add("d-none");
      resultDiv.textContent = "";
      resultDiv.className = "alert alert-secondary mt-3 d-none";
      feedbackSection.classList.add("d-none");
  
      // Send URL to Flask backend
      fetch("http://127.0.0.1:5000/predict-only", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ url: currentUrl })
      })
        .then(response => response.json())
        .then(data => {
          if (data.result) {
            const label = data.result.toLowerCase();
            resultDiv.classList.remove("d-none");
            resultDiv.classList.add(label === "phishing" ? "alert-danger" : "alert-success");
            resultDiv.textContent = `The site is ${label.toUpperCase()}.`;
  
            // Save the record ID for feedback later
            currentRecordId = data.id;
  
            // Show feedback section
            feedbackSection.classList.remove("d-none");
          } else if (data.error) {
            showError(data.error);
          }
        })
        .catch(err => showError("Server Error: " + err.message));
    });
  
    function showError(msg) {
      resultDiv.className = "alert alert-warning mt-3";
      resultDiv.textContent = msg;
      resultDiv.classList.remove("d-none");
    }
  
    feedbackButtons.forEach(button => {
      button.addEventListener("click", function () {
        const feedback = this.dataset.feedback;
  
        if (!currentRecordId) {
          feedbackSection.innerHTML = `<div class="text-danger small mt-2">⚠️ Missing record ID!</div>`;
          return;
        }
  
        fetch(`http://127.0.0.1:5000/feedback/${currentRecordId}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ feedback })
        })
          .then(response => response.json())
          .then(() => {
            feedbackSection.innerHTML = `<div class="text-success small mt-2">✅ Thanks for your feedback!</div>`;
          })
          .catch(err => {
            feedbackSection.innerHTML = `<div class="text-danger small mt-2">⚠️ Failed to send feedback.</div>`;
            console.error("Feedback error:", err);
          });
      });
    });
  });
  