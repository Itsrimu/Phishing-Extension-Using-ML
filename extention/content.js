// Log that the content script is loaded
console.log("Phishing Detection content script loaded");

// Function to send the URL of the page to the background script
function sendPageUrl() {
  const currentUrl = window.location.href;

  // Send the URL to the background script for prediction
  chrome.runtime.sendMessage({ action: 'check_url', url: currentUrl }, function (response) {
    console.log('Phishing Check Response:', response);
  });
}

// Call the function to send the page URL
sendPageUrl();

// Add an event listener for user feedback (e.g., a button click on the page)
document.addEventListener('click', function (event) {
  if (event.target && event.target.matches('.feedback-btn')) {
    const feedback = event.target.dataset.feedback; // Assuming button has data-feedback attribute
    const currentUrl = window.location.href;
    
    // Send feedback to the background script (for storage or processing)
    chrome.runtime.sendMessage({ action: 'store_feedback', url: currentUrl, feedback: feedback }, function (response) {
      console.log('Feedback sent:', response);
    });
  }
});
