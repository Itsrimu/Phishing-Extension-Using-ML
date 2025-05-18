document.addEventListener("DOMContentLoaded", function () {
  const autoDetectCheckbox = document.getElementById("autoDetect");
  const resetSettingsBtn = document.getElementById("reset-settings");

  // Load saved settings
  chrome.storage.local.get(["autoDetectEnabled"], function (result) {
    autoDetectCheckbox.checked = result.autoDetectEnabled || false;
  });

  // Toggle Auto-Detection setting
  autoDetectCheckbox.addEventListener("change", () => {
    const autoDetectEnabled = autoDetectCheckbox.checked;
    chrome.storage.local.set({ autoDetectEnabled }, () => {
      alert(` Auto-Detection ${autoDetectEnabled ? "Enabled" : "Disabled"}`);
    });
  });

  // Reset settings to default
  resetSettingsBtn.addEventListener("click", () => {
    chrome.storage.local.set({ autoDetectEnabled: false }, () => {
      autoDetectCheckbox.checked = false;
      alert(" Settings reset to default.");
    });
  });
});
