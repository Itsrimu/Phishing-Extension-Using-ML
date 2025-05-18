// Log that the content script is loaded
console.log(" Phishing Detection content script loaded");

// Function to send the current page URL to the background script
function sendPageUrl() {
  const currentUrl = window.location.href;

  // Send a message to background script to check this URL
  chrome.runtime.sendMessage({ action: 'check_url', url: currentUrl }, function (response) {
    console.log(' Phishing Check Response:', response);
  });
}

// Send page URL on load
sendPageUrl();

// Listen for user feedback button clicks on the page itself
document.addEventListener('click', function (event) {
  const target = event.target;

  if (target && target.matches('.feedback-btn')) {
    const feedback = target.dataset.feedback; // Requires: data-feedback="correct"/"incorrect"
    const currentUrl = window.location.href;

    // Send feedback to background script
    chrome.runtime.sendMessage(
      {
        action: 'store_feedback',
        url: currentUrl,
        feedback: feedback
      },
      function (response) {
        console.log(' Feedback sent:', response);
      }
    );
  }
});

// Listen for messages from the background script to show alerts or take further actions
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'show_alert') {
    // Show a phishing warning if the site is detected as phishing
    if (message.isPhishing) {
      alert('⚠️ Warning: This site is potentially a phishing site!');
    }
  }
});
