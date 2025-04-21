// background.js

// Fired when the extension is first installed
chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension installed successfully.");
  });
  
  // Listen for messages from popup.js or other parts of the extension
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === "getCurrentTabUrl") {
      // Query the current active tab in the focused window
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        if (activeTab && activeTab.url) {
          sendResponse({ url: activeTab.url });
        } else {
          sendResponse({ error: "Could not retrieve the active tab URL." });
        }
      });
  
      // Keep the message channel open for the async response
      return true;
    }
  });
  