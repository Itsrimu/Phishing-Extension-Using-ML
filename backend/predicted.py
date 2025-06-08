# File: backend/predicted.py

import pickle
from pathlib import Path
from features import extract_url_features

# Paths
MODEL_PATH = Path("model/phishing_model1.pkl")
VECTORIZER_PATH = Path("model/vectorizer1.pkl")

def load_model_and_vectorizer():
    if not MODEL_PATH.exists() or not VECTORIZER_PATH.exists():
        raise FileNotFoundError("Model or vectorizer file not found.")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

def predict_url(url: str):
    model, vectorizer = load_model_and_vectorizer()
    features = extract_url_features(url)
    if not isinstance(features, dict):
        raise ValueError("Feature extraction did not return a dict.")
    try:
        features_vectorized = vectorizer.transform([features])
    except Exception as e:
        raise ValueError(f"Vectorizer transform failed: {e}")
    prediction = model.predict(features_vectorized)[0]
    label = "bad" if prediction == 1 else "good"
    return label

if __name__ == "__main__":
    url = input("🔗 Enter a URL to check: ").strip()
    if not url:
        print("No URL entered.")
    else:
        try:
            prediction = predict_url(url)
            print(f"Prediction: {prediction.upper()}")
        except Exception as e:
            print("Prediction failed:", e)