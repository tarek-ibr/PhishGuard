const form = document.getElementById('news-form');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const input = document.getElementById('news-text').value;

  try {
    const response = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: input })  // ✅ Correct: sending raw URL
    });

    const resultDiv = document.getElementById('prediction-result');

    if (response.ok) {
      const data = await response.json();

      if (data.prediction !== undefined) {
        resultDiv.innerText = data.prediction === 0
          ? '✅ This URL is Safe'
          : '🚨 This URL is Phishing';
      } else {
        resultDiv.innerText = '⚠️ Error: ' + (data.error || 'Unexpected response format');
      }
    } else {
      resultDiv.innerText = '⚠️ Server returned error: ' + response.status;
    }
  } catch (error) {
    const resultDiv = document.getElementById('prediction-result');
    resultDiv.innerText = '⚠️ Request failed: ' + error.message;
  }
});
