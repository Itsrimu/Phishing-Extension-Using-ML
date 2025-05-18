from flask import Blueprint, request, jsonify
from predict import predict_url
from database import insert_prediction
import logging

prediction_bp = Blueprint('prediction', __name__)

# Setup logging
logging.basicConfig(
    filename="logs/prediction_routes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_request(action, url=None, record_id=None, error=None):
    """Centralized logging for API actions."""
    message = f"{action} | URL: {url}" if url else f"{action} | ID: {record_id}"
    if error:
        message += f" | Error: {error}"
        logging.error(message)
    else:
        logging.info(message)

@prediction_bp.route("/", methods=["POST"])
def predict():
    """
    Predicts whether a URL is phishing or legitimate and stores the result.
    """
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        prediction_data = predict_url(url)  # Now returns a dictionary
        label = prediction_data["verdict"].lower()  # Extract `verdict` correctly
        confidence = prediction_data["confidence_score"]

        doc_id = insert_prediction(url, label)  # Store the label in lowercase

        log_request("Prediction", url=url, record_id=doc_id)

        response_data = {
            "url": url,
            "result": label,
            "id": str(doc_id),
            "confidence": confidence
        }

        return jsonify(response_data), 200

    except Exception as e:
        log_request("Prediction Failed", url=url, error=str(e))
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
