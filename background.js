chrome.webNavigation.onBeforeNavigate.addListener(
  async function(details) {
    const url = details.url;
    
    // Skip checking for local/internal URLs and extension pages
    if (url.startsWith('chrome://') || 
        url.startsWith('chrome-extension://') || 
        url.startsWith('moz-extension://') ||
        url.startsWith('localhost') || 
        url.startsWith('127.0.0.1') ||
        url.startsWith('file://') ||
        url.includes('warning.html')) {
      console.log('Skipping URL (internal/local):', url);
      return;
    }

    // Skip if this is already a warning page
    if (url.includes(chrome.runtime.getURL('warning.html'))) {
      console.log('Skipping URL (warning page):', url);
      return;
    }

    console.log('🔍 AUTOMATIC CHECK - Checking URL:', url);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
      });

      if (!response.ok) {
        console.error('❌ Server error:', response.status, response.statusText);
        console.log('✅ Allowing navigation due to server error');
        return;
      }

      const data = await response.json();
      console.log('📊 API Response for', url, ':', data);
      
      // Validate prediction value
      if (data.prediction === undefined || data.prediction === null) {
        console.error('❌ Invalid prediction response:', data);
        console.log('✅ Allowing navigation due to invalid response');
        return;
      }

      // According to user clarification: prediction 1 = safe, prediction 0 = phishing
      const predictionValue = data.prediction;
      const isSafe = predictionValue === 1;
      const isPhishing = predictionValue === 0;
      
      console.log('🎯 Prediction Analysis:');
      console.log('   - Raw prediction value:', predictionValue);
      console.log('   - Is Safe (prediction === 1):', isSafe);
      console.log('   - Is Phishing (prediction === 0):', isPhishing);

      if (isSafe) {
        console.log('✅ URL is SAFE - Allowing normal navigation to:', url);
        // Do nothing - let the normal navigation proceed
        return;
      } else if (isPhishing) {
        console.log('🚨 URL is PHISHING - Redirecting to warning page');
        // Show warning and ask user if they want to proceed
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
          const activeTab = tabs[0];
          if (activeTab && activeTab.id) {
            chrome.tabs.update(activeTab.id, {
              url: chrome.runtime.getURL('warning.html') + '?destination=' + encodeURIComponent(url)
            });
          }
        });
      } else {
        console.warn('⚠️ Unexpected prediction value:', predictionValue);
        console.log('✅ Allowing navigation due to unexpected prediction value');
        // For safety, allow navigation if we get an unexpected value
        return;
      }
    } catch (error) {
      console.error('❌ Error checking URL:', error);
      console.log('✅ Allowing navigation due to error');
      // If the backend is not available, don't block navigation
      return;
    }
  },
  { url: [{schemes: ['http', 'https']}] }
);

// Listen for messages from popup.js or warning.html
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "checkUrl") {
    fetchPrediction(message.url)
      .then(result => {
        console.log('Prediction result for popup:', result);
        sendResponse(result);
      })
      .catch(error => {
        console.error('Error in popup prediction:', error);
        sendResponse({error: error.toString()});
      });
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
    
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('fetchPrediction result:', result);
    return result;
  } catch (error) {
    console.error('fetchPrediction error:', error);
    throw new Error(`Failed to check URL: ${error.message}`);
  }
}
