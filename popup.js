document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('news-form');
  const resultDiv = document.getElementById('prediction-result');

  // Check current tab URL for automatic checking
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    const currentTab = tabs[0];
    if (currentTab && currentTab.url) {
      if (currentTab.url.startsWith('http')) {
        document.getElementById('news-text').value = currentTab.url;
      }
    }
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const input = document.getElementById('news-text').value;
    if (!input) {
      resultDiv.innerText = '⚠️ Please enter a URL to check';
      return;
    }
    
    // Add loading indicator
    resultDiv.innerText = 'Checking URL...';
    
    try {
      // Try to use the background script's helper function via messaging
      chrome.runtime.sendMessage(
        { action: "checkUrl", url: input }, 
        function(response) {
          if (chrome.runtime.lastError) {
            // If background script isn't available, fall back to direct API call
            fetchDirectly(input);
            return;
          }
          
          if (response.error) {
            resultDiv.innerText = '⚠️ Error: ' + response.error;
            return;
          }
          
          if (response.prediction !== undefined) {
            resultDiv.innerText = response.prediction === 0
              ? '✅ This URL is Safe'
              : '🚨 This URL is Phishing';
          } else {
            resultDiv.innerText = '⚠️ Error: Unexpected response format';
          }
        }
      );
    } catch (error) {
      resultDiv.innerText = '⚠️ Error: ' + error.message;
    }
  });
  
  // Fallback function to call API directly if messaging fails
  async function fetchDirectly(url) {
    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });
      
      if (!response.ok) {
        resultDiv.innerText = '⚠️ Server error: ' + response.status;
        return;
      }
      
      const data = await response.json();
      if (data.prediction !== undefined) {
        resultDiv.innerText = data.prediction === 0
          ? '✅ This URL is Safe'
          : '🚨 This URL is Phishing';
      } else {
        resultDiv.innerText = '⚠️ Error: ' + (data.error || 'Unexpected response format');
      }
    } catch (error) {
      resultDiv.innerText = '⚠️ Server unavailable. Make sure the backend is running on localhost:5000';
    }
  }
});
