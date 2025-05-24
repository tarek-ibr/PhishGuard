document.addEventListener('DOMContentLoaded', function () {
  const urlParams = new URLSearchParams(window.location.search);
  const destination = urlParams.get('destination');
  const urlDisplay = document.getElementById('suspicious-url');
  const proceedBtn = document.getElementById('proceed-anyway');
  const goBackBtn = document.getElementById('go-back');
  const statusMessage = document.getElementById('status-message');

  console.log('Warning page loaded, destination:', destination);

  // Default values
  urlDisplay.textContent = 'Unknown URL';
  proceedBtn.disabled = true;

  if (destination) {
    try {
      const decodedUrl = decodeURIComponent(destination);
      console.log('Decoded URL:', decodedUrl);

      const validUrl = new URL(decodedUrl);
      console.log('Valid URL object created:', validUrl.href);

      urlDisplay.textContent = validUrl.href;
      statusMessage.textContent = 'URL validation: Valid URL format';
      statusMessage.style.color = '#2e7d32';
      proceedBtn.disabled = false;

      proceedBtn.addEventListener('click', async () => {
        try {
          await chrome.runtime.sendMessage({ action: 'bypassUrl', url: validUrl.href });
        } catch (e) {
          console.warn('Could not register bypass, proceeding anyway', e);
        }
        window.location.href = validUrl.href;
      });


    } catch (e) {
      console.error('URL validation error:', e);
      urlDisplay.textContent = 'Invalid or unsafe URL: ' + (destination || 'null');
      statusMessage.textContent = 'URL validation: Invalid URL format';
      statusMessage.style.color = '#d32f2f';
      proceedBtn.disabled = true;
    }
  } else {
    console.warn('No destination URL provided');
    urlDisplay.textContent = 'No URL provided';
    statusMessage.textContent = 'Error: No destination URL specified';
    statusMessage.style.color = '#d32f2f';
    proceedBtn.disabled = true;
  }

  goBackBtn.addEventListener('click', function () {
    console.log('Going back safely');
    statusMessage.textContent = 'Going back to safety...';
    statusMessage.style.color = '#2e7d32';

    try {
      if (window.history.length > 1) {
        window.history.back();
      } else {
        window.location.href = 'https://www.google.com';
      }
    } catch (e) {
      console.error('Error going back:', e);
      window.location.href = 'https://www.google.com';
    }
  });
});
