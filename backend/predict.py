import pickle
import logging
from pathlib import Path
from feature import extract_url_features

# Enable logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Path to the saved model pipeline
MODEL_PATH = Path("model/phishing_model1.pkl")

def load_model():
    """
    Load the saved machine learning model pipeline.
    """
    try:
        with open(MODEL_PATH, "rb") as file:
            model = pickle.load(file)
        logging.info(" Model loaded successfully.")
        return model
    except FileNotFoundError:
        logging.error(f" Model file missing: {MODEL_PATH}")
        raise FileNotFoundError(f"Model not found at path: {MODEL_PATH}")
    except Exception as e:
        logging.error(f" Error loading model: {e}")
        raise Exception(f"Error loading model: {e}")

def predict_url(url: str) -> dict:
    """
    Predict whether the URL is phishing or legitimate.

    Args:
        url (str): The URL to be analyzed.

    Returns:
        dict: Contains prediction label and confidence score.
    """
    try:
        logging.info(f" Extracting features for URL: {url}")
        features = extract_url_features(url)

        if not isinstance(features, dict) or not features:
            logging.error(" Feature extraction failed or returned an empty dictionary.")
            raise ValueError("Feature extraction failed or returned invalid data.")

        model = load_model()

        # Ensure model receives valid input format
        model_input = {k: v for k, v in features.items() if isinstance(v, (int, float, bool))}

        prediction_proba = model.predict_proba([model_input])[0]
        prediction = model.predict([model_input])[0]

        confidence = round(max(prediction_proba) * 100, 2)
        label = "Phishing" if prediction == 1 else "Legitimate"

        logging.info(f" Prediction: {label} ({confidence}% confidence)")

        return {"url": url, "verdict": label, "confidence_score": f"{confidence}%"}

    except Exception as e:
        logging.error(f" Prediction failed for {url}: {e}")
        raise Exception(f"Prediction failed: {e}")

if __name__ == "__main__":
    test_url = input("Enter a URL to check: ").strip()
    try:
        result = predict_url(test_url)
        print(f"\n URL Analysis Result:")
        print(f" Confidence Score: {result['confidence_score']}")
        print(f" Verdict: {result['verdict']}")
    except Exception as err:
        print(f" Error: {err}")
