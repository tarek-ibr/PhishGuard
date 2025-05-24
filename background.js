chrome.webNavigation.onBeforeNavigate.addListener(
  async function(details) {
    const url = details.url;
    
    // Skip checking for local/internal URLs
    if (url.startsWith('chrome://') || url.startsWith('chrome-extension://') || 
        url.startsWith('localhost') || url.startsWith('127.0.0.1')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })  // Send raw URL as expected by backend
      });

      if (!response.ok) {
        console.error('Server error:', response.status);
        return;
      }

      const data = await response.json();
      const isPhishing = data.prediction === 0;

      if (isPhishing) {
        // Show warning and ask user if they want to proceed
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          const activeTab = tabs[0];
          chrome.tabs.update(activeTab.id, {
            url: chrome.runtime.getURL('warning.html') + '?destination=' + encodeURIComponent(url)
          });
        });
      }
    } catch (error) {
      console.error('Error checking URL:', error);
    }
  },
  { url: [{schemes: ['http', 'https']}] }
);

// Listen for messages from popup.js or warning.html
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "checkUrl") {
    fetchPrediction(message.url)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({error: error.toString()}));
    return true; // Required for async sendResponse
  }
});

// Helper function to check URLs (can be used by popup.js as well)
async function fetchPrediction(url) {
  try {
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    });
    
    return await response.json();
  } catch (error) {
    throw new Error(`Failed to check URL: ${error.message}`);
  }
}
