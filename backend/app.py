from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load ML model and vectorizer
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('vector.pkl', 'rb') as f:
    vectorizer = pickle.load(f)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No JSON received'}), 400

    # Case 1: text input (for fake news)
    if 'text' in data:
        text = data['text']
        text_transformed = vectorizer.transform([text])
        prediction = model.predict(text_transformed)[0]
        return jsonify({'prediction': int(prediction)})

    # Case 2: URL features (for phishing detection)
    elif 'features' in data:
        features = data['features']
        feature_array = [
            features.get('length', 0),
            features.get('hostnameLength', 0),
            features.get('pathLength', 0),
            int(features.get('hasIPAddress', False)),
            features.get('numSpecialChars', 0)
        ]
        prediction = model.predict([feature_array])[0]
        return jsonify({'prediction': int(prediction)})

    return jsonify({'error': 'Missing expected keys'}), 400


if __name__ == '__main__':
    app.run(debug=True)
