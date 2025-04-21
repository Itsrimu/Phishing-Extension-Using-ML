# File: backend/predict.py

import pickle
from pathlib import Path
from feature import extract_url_features
from train_model import update_model_with_feedback

# Paths
MODEL_PATH = Path("model/phishing_model1.pkl")
VECTORIZER_PATH = Path("model/vectorizer1.pkl")

# Load model and vectorizer
def load_model_and_vectorizer():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    return model, vectorizer

# Predict if URL is phishing or legitimate
def predict_url(url: str):
    model, vectorizer = load_model_and_vectorizer()
    features = extract_url_features(url)
    features_vectorized = vectorizer.transform([features])
    prediction = model.predict(features_vectorized)[0]
    label = "bad" if prediction == 1 else "good"
    return label

# Update model with user feedback
def update_model(url: str, feedback: str):
    try:
        update_model_with_feedback(url, feedback)
        print("Model updated with feedback.")
    except Exception as e:
        print(" Failed to update model:", e)

# Example usage
if __name__ == "__main__":
    url = input("🔗 Enter a URL to check: ")
    prediction = predict_url(url)
    print(f"Prediction: {prediction.upper()}")

    feedback = input(" Was this correct? (yes/no): ").strip().lower()
    if feedback == "no":
        correct_label = input(" Then what should it be? (good/bad): ").strip().lower()
        if correct_label in ["good", "bad"]:
            update_model(url, correct_label)
        else:
            print("⚠ Invalid feedback. Must be 'good' or 'bad'.")
