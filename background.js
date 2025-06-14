// background.js

chrome.webNavigation.onBeforeNavigate.addListener(async function (details) {

  const { tabId, url } = details;

  /* 0️⃣ Skip if the user has already allowed this URL in this tab */
  if (bypassMap.has(tabId) && bypassMap.get(tabId).has(url)) {
    console.log('User-approved navigation, skipping phishing check:', url);
    return;
  }

  // Skip internal/local URLs
  if (
    url.startsWith('chrome://') ||
    url.startsWith('chrome-extension://') ||
    url.startsWith('moz-extension://') ||
    url.startsWith('localhost') ||
    url.startsWith('127.0.0.1') ||
    url.startsWith('file://') ||
    url.includes('warning.html') ||
    url.includes(chrome.runtime.getURL('warning.html'))
  ) {
    console.log('Skipping internal/local URL:', url);
    return;
  }

  console.log('🔍 Checking URL:', url);

  try {
    const result = await fetchPrediction(url);

    if (!result || typeof result.prediction !== 'number') {
      console.warn('Invalid or missing prediction from API. Allowing navigation.');
      return;
    }

    const isPhishing = result.prediction === 0;

    if (isPhishing) {
      console.log('🚨 Phishing detected! Redirecting to warning page.');
      chrome.tabs.update(details.tabId, {
        url: chrome.runtime.getURL('warning.html') + '?destination=' + encodeURIComponent(url)
      });
    } else {
      console.log('✅ Safe URL. No action taken.');
    }
  } catch (error) {
    console.error('❌ Error during phishing check:', error);
    // Fail-open: allow navigation in case of error
  }
}, {
  url: [{ schemes: ['http', 'https'] }]
});

// Message listener for popup.js or warning.html
// background.js  (top-level)
const bypassMap = new Map();  // tabId → Set<String> of URLs (or domains)

/*  Exchange messages with warning.html
----------------------------------------------------*/
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'bypassUrl' && sender.tab) {
    const { id: tabId } = sender.tab;
    if (!bypassMap.has(tabId)) bypassMap.set(tabId, new Set());
    bypassMap.get(tabId).add(msg.url);
    console.log(`✅ User bypassed for ${msg.url} in tab ${tabId}`);
    sendResponse({ ok: true });
    return;               // no async work, keep channel closed
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  bypassMap.delete(tabId);
});


// Reusable function to fetch prediction
async function fetchPrediction(url) {
  // ✅ Remove trailing slashes before sending to the backend
  const cleanedUrl = url.replace(/\/+$/, '');

  try {
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: cleanedUrl })
    });

    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    return result;

  } catch (error) {
    console.error('fetchPrediction error:', error);
    throw new Error(`Failed to check URL: ${error.message}`);
  }
}

