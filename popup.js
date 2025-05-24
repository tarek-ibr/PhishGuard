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
    
    const input = document.getElementById('news-text').value.trim();
    if (!input) {
      resultDiv.innerText = '⚠️ Please enter a URL to check';
      return;
    }
    
    // Validate URL format
    try {
      new URL(input);
    } catch (e) {
      resultDiv.innerText = '⚠️ Please enter a valid URL (including http:// or https://)';
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
            console.error('Chrome runtime error:', chrome.runtime.lastError);
            // If background script isn't available, fall back to direct API call
            fetchDirectly(input);
            return;
          }
          
          if (response.error) {
            console.error('Response error:', response.error);
            resultDiv.innerText = '⚠️ Error: ' + response.error;
            return;
          }
          
          console.log('Popup received response:', response);
          
          if (response.prediction !== undefined) {
            // According to user clarification: prediction 1 = safe, prediction 0 = phishing
            const isSafe = response.prediction === 1;
            const isPhishing = response.prediction === 0;
            
            if (isSafe) {
              resultDiv.innerText = '✅ This URL is Safe';
              resultDiv.style.color = '#2e7d32';
            } else if (isPhishing) {
              resultDiv.innerText = '🚨 This URL is Phishing';
              resultDiv.style.color = '#d32f2f';
            } else {
              resultDiv.innerText = '⚠️ Unknown prediction value: ' + response.prediction;
              resultDiv.style.color = '#ff9800';
            }
          } else {
            console.error('Unexpected response format:', response);
            resultDiv.innerText = '⚠️ Error: Unexpected response format';
          }
        }
      );
    } catch (error) {
      console.error('Error in form submission:', error);
      resultDiv.innerText = '⚠️ Error: ' + error.message;
    }
  });
  
  // Fallback function to call API directly if messaging fails
  async function fetchDirectly(url) {
    try {
      console.log('Calling API directly for URL:', url);
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url })
      });
      
      if (!response.ok) {
        resultDiv.innerText = '⚠️ Server error: ' + response.status + ' ' + response.statusText;
        return;
      }
      
      const data = await response.json();
      console.log('Direct API response:', data);
      
      if (data.prediction !== undefined) {
        // According to user clarification: prediction 1 = safe, prediction 0 = phishing
        const isSafe = data.prediction === 1;
        const isPhishing = data.prediction === 0;
        
        if (isSafe) {
          resultDiv.innerText = '✅ This URL is Safe';
          resultDiv.style.color = '#2e7d32';
        } else if (isPhishing) {
          resultDiv.innerText = '🚨 This URL is Phishing';
          resultDiv.style.color = '#d32f2f';
        } else {
          resultDiv.innerText = '⚠️ Unknown prediction value: ' + data.prediction;
          resultDiv.style.color = '#ff9800';
        }
      } else if (data.error) {
        resultDiv.innerText = '⚠️ Error: ' + data.error;
      } else {
        console.error('Unexpected API response:', data);
        resultDiv.innerText = '⚠️ Error: Unexpected response format';
      }
    } catch (error) {
      console.error('Direct API error:', error);
      resultDiv.innerText = '⚠️ Server unavailable. Make sure the backend is running on localhost:5000';
    }
  }
});
