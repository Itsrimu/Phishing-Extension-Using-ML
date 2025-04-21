# File: routes/predict_routes.py

from flask import Blueprint, request, jsonify
from predict import predict_url
from database import insert_prediction
import logging

prediction_bp = Blueprint('prediction', __name__)

# Setup logging
logging.basicConfig(
    filename="logs/prediction_routes.log",  # Optionally create a "logs" directory
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@prediction_bp.route("/", methods=["POST"])
def predict_route():
    """
    Predicts whether a URL is phishing or safe, and stores the result.
    """
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        prediction = predict_url(url)
        label = "phishing" if prediction == 1 else "safe"

        # Store in DB (without feedback)
        doc_id = insert_prediction(url, label)

        # Log the prediction
        logging.info(f" Prediction | URL: {url} → {label} | ID: {doc_id}")

        return jsonify({
            "url": url,
            "result": label,
            "id": str(doc_id)
        }), 200

    except Exception as e:
        logging.error(f" Prediction failed for {url}: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
