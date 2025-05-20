from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import tensorflow as tf
import numpy as np
from features import extract_all_features_df

app = Flask(__name__)
CORS(app)

# Load the bundled model with scaler and feature names
print("Loading model bundle...")
bundle = joblib.load('phishing_model_bundle.pkl')
model_bytes = bundle['model_bytes']
scaler = bundle['scaler']
feature_names = bundle['feature_names']

# Reconstruct the model from saved bytes
with open('temp_model.keras', 'wb') as f:
    f.write(model_bytes)
model = tf.keras.models.load_model('temp_model.keras')

print("Model loaded successfully")


@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'message': 'PhishGuard API is running. Use /predict endpoint to check URLs.'
    })


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    # Case: phishing detection by URL
    if 'url' in data:
        url = data['url']
        try:
            # Extract features
            features_df = extract_all_features_df(url)

            # Ensure the features match the expected feature names
            features_df = features_df[feature_names]

            # Apply the scaler
            scaled_features = scaler.transform(features_df)

            # Make prediction
            prediction = model.predict(scaled_features)
            prediction = int(np.round(prediction[0][0]))  # Convert to binary prediction

            return jsonify({'prediction': prediction})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Missing \"url\" key in request'}), 400


if __name__ == '__main__':
    app.run(debug=True)