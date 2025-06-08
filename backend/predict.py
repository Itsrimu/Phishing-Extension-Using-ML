import pickle
import logging
from pathlib import Path
from features import extract_url_features  # <-- FIXED import

# Enable logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Path to the saved model pipeline
MODEL_PATH = Path("model/phishing_model1.pkl")

def load_model(context=None):
    """
    Load the saved machine learning model pipeline.
    Accepts an optional argument for compatibility with Flask reload behavior.
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
        dict: Contains analysis result (label only).
    """
    try:
        logging.info(f" Extracting features for URL: {url}")
        features = extract_url_features(url)

        if not isinstance(features, dict) or not features:
            logging.error(" Feature extraction failed or returned an empty dictionary.")
            raise ValueError("Feature extraction failed or returned invalid data.")

        model = load_model()

        # Pass a list of dicts to the pipeline (DictVectorizer expects this)
        prediction = model.predict([features])[0]
        label = "Phishing" if prediction == 1 else "Legitimate"

        # Optionally, get confidence score if available
        confidence = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba([features])[0]
            confidence = round(max(proba) * 100, 2)

        logging.info(f" Analysis Result: {label}")

        result = {"url": url, "analysis_result": label}
        if confidence is not None:
            result["confidence"] = f"{confidence}%"
        return result

    except Exception as e:
        logging.error(f" Prediction failed for {url}: {e}")
        raise Exception(f"Prediction failed: {e}")

if __name__ == "__main__":
    test_url = input("Enter a URL to check: ").strip()
    try:
        result = predict_url(test_url)
        print(f"\n URL Analysis Result:")
        print(f" Analysis Result: {result['analysis_result']}")
        if "confidence" in result:
            print(f" Confidence: {result['confidence']}")
    except Exception as err:
        print(f" Error: {err}")
