document.addEventListener("DOMContentLoaded", () => {
  const $ = id => document.getElementById(id);

  const autoDetectCheckbox = $("autoDetect");
  const darkModeCheckbox = $("darkMode");
  const sensitivitySlider = $("sensitivity");
  const sensitivityValue = $("sensitivity-value");
  const blocklistInput = $("blocklistInput");
  const addBlocklistBtn = $("add-blocklist");
  const blocklist = $("blocklist");
  const apiKeyInput = $("apiKeyInput");
  const saveApiKeyBtn = $("save-api-key");
  const resetSettingsBtn = $("reset-settings");

  const statusText = document.createElement("p");
  statusText.className = "status-message fade-in";
  document.body.appendChild(statusText);

  // Load stored settings
  chrome.storage.local.get(
    ["autoDetectEnabled", "darkModeEnabled", "sensitivity", "blocklist", "apiKey"],
    ({ autoDetectEnabled = false, darkModeEnabled = false, sensitivity = 70, blocklist: savedList = [], apiKey = "" }) => {
      autoDetectCheckbox.checked = autoDetectEnabled;
      darkModeCheckbox.checked = darkModeEnabled;
      sensitivitySlider.value = sensitivity;
      sensitivityValue.textContent = `Current: ${sensitivity}%`;
      apiKeyInput.value = apiKey;

      document.body.classList.toggle("dark-theme", darkModeEnabled);
      savedList.forEach(site => addBlocklistItem(site));
    }
  );

  // Event Listeners
  autoDetectCheckbox.addEventListener("change", () => {
    chrome.storage.local.set({ autoDetectEnabled: autoDetectCheckbox.checked });
    showStatus(`Auto-Detection ${autoDetectCheckbox.checked ? "Enabled" : "Disabled"}`);
  });

  darkModeCheckbox.addEventListener("change", () => {
    const enabled = darkModeCheckbox.checked;
    document.body.classList.toggle("dark-theme", enabled);
    chrome.storage.local.set({ darkModeEnabled: enabled });
    showStatus(`Dark Mode ${enabled ? "Enabled" : "Disabled"}`);
  });

  sensitivitySlider.addEventListener("input", () => {
    const value = sensitivitySlider.value;
    sensitivityValue.textContent = `Current: ${value}%`;
    chrome.storage.local.set({ sensitivity: Number(value) });
    showStatus(`Detection sensitivity set to ${value}%`);
  });

  addBlocklistBtn.addEventListener("click", () => {
    const site = blocklistInput.value.trim().toLowerCase();
    if (!site) return;

    chrome.storage.local.get(["blocklist"], ({ blocklist = [] }) => {
      if (!blocklist.includes(site)) {
        blocklist.push(site);
        chrome.storage.local.set({ blocklist });
        addBlocklistItem(site);
        showStatus(`Added ${site} to blocklist.`);
        blocklistInput.value = "";
      }
    });
  });

  saveApiKeyBtn.addEventListener("click", () => {
    const apiKey = apiKeyInput.value.trim();
    if (apiKey) {
      chrome.storage.local.set({ apiKey }, () => {
        showStatus("✅ WHOIS API Key saved.");
      });
    }
  });

  resetSettingsBtn.addEventListener("click", () => {
    chrome.storage.local.set({
      autoDetectEnabled: false,
      darkModeEnabled: false,
      sensitivity: 70,
      blocklist: [],
      apiKey: ""
    }, () => {
      autoDetectCheckbox.checked = false;
      darkModeCheckbox.checked = false;
      sensitivitySlider.value = 70;
      sensitivityValue.textContent = "Current: 70%";
      apiKeyInput.value = "";
      document.body.classList.remove("dark-theme");
      blocklist.innerHTML = "";
      showStatus("Settings reset to default.");
    });
  });

  function addBlocklistItem(site) {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex justify-content-between align-items-center";
    li.textContent = site;

    const removeBtn = document.createElement("button");
    removeBtn.textContent = "❌";
    removeBtn.className = "remove-block";
    removeBtn.onclick = () => removeBlocklistItem(site, li);

    li.appendChild(removeBtn);
    blocklist.appendChild(li);
  }

  function removeBlocklistItem(site, element) {
    chrome.storage.local.get(["blocklist"], ({ blocklist = [] }) => {
      const updatedList = blocklist.filter(item => item !== site);
      chrome.storage.local.set({ blocklist: updatedList }, () => {
        element.remove();
        showStatus(`Removed ${site} from blocklist.`);
      });
    });
  }

  function showStatus(message) {
    statusText.textContent = message;
    statusText.style.opacity = 1;
    setTimeout(() => (statusText.style.opacity = 0), 3000);
  }
});
