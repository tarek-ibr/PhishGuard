from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd
import tensorflow as tf
import numpy as np
from features import extract_all_features_df

app = Flask(__name__)
CORS(app)

print("Loading model bundle...")
bundle = joblib.load('phishing_model_bundle.pkl')

model = tf.keras.models.load_model('phishing_model.keras')

scaler = bundle['scaler']
feature_names = bundle['feature_names']

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

            from urllib.parse import urlparse, urlunparse

            # 1️⃣  Make sure we have a scheme so that urlparse works reliably.
            if not url.lower().startswith(("http://", "https://")):
                url = "http://" + url

            # 2️⃣  Parse the URL.
            p = urlparse(url)

            # 3️⃣  If the netloc is empty (e.g. user passed just “example.com/foo”)
            #     urlparse puts everything in `path`, so fix that.
            netloc = p.netloc or p.path.split("/")[0]

            # 4️⃣  Add “www.” if missing.
            if not netloc.startswith("www."):
                netloc = "www." + netloc

            # 5️⃣  Re-assemble, blanking out path/params/query/fragment.
            cleaned = urlunparse((p.scheme, netloc, "", "", "", ""))

            # Extract features
            newDF = extract_all_features_df(cleaned)
            features_df = newDF[feature_names]

            cols_to_transform = ['URLLength', 'DomainLength', 'TLDLength', 'NoOfObfuscatedChar', 'ObfuscationRatio',
                                 'DegitRatioInURL', 'NoOfEqualsInURL', 'NoOfQMarkInURL', 'NoOfAmpersandInURL',
                                 'SpacialCharRatioInURL']

            # Step 5: Apply log1p transformation
            features_df[cols_to_transform] = features_df[cols_to_transform].apply(lambda col: np.log1p(col))

            scaled_features = scaler.transform(features_df)

            # Make prediction
            prediction = model.predict(scaled_features)
            prediction = (prediction > 0.5).astype(int)

            prediction = prediction.tolist()
            prediction = prediction[0][0]

            print(prediction)

            return jsonify({'prediction': prediction})
        except Exception as e:
            return jsonify({'Error': str(e)}), 500

    return jsonify({'error': 'Missing \"url\" key in request'}), 400


if __name__ == '__main__':
    app.run(debug=True)