from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import pandas as pd
from features import extract_all_features_df  # ← Import your function

app = Flask(__name__)
CORS(app)

# Load your ML model
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    # Case: phishing detection by URL
    if 'url' in data:
        url = data['url']
        try:
            features_df = extract_all_features_df(url)
            prediction = model.predict(features_df)[0]
            return jsonify({'prediction': int(prediction)})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Missing \"url\" key in request'}), 400

if __name__ == '__main__':
    app.run(debug=True)
