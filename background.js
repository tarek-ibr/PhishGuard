chrome.webRequest.onBeforeRequest.addListener(
  async function(details) {
    const url = details.url;

    const features = extractUrlFeatures(url);

    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ features: features })
    });

    const data = await response.json();
    const isPhishing = data.prediction === 1;

    if (isPhishing) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'img/icon128.jpg',
        title: 'Phishing Detected!',
        message: `Blocked access to: ${url}`
      });
      return { cancel: true };
    }

    return { cancel: false };
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);

// Feature extraction
function extractUrlFeatures(url) {
  const a = document.createElement('a');
  a.href = url;

  return {
    length: url.length,
    hostnameLength: a.hostname.length,
    pathLength: a.pathname.length,
    hasIPAddress: /^\d{1,3}(\\.\\d{1,3}){3}$/.test(a.hostname),
    numSpecialChars: (url.match(/[-_.~!$&'()*+,;=:@]/g) || []).length
  };
}
