# File: routes/feedback_routes.py

from flask import Blueprint, request, jsonify
from database import insert_prediction, update_feedback, get_all_predictions, get_prediction_by_id
from predict import predict_url
import logging

# Create a Blueprint for feedback routes
feedback_bp = Blueprint('feedback', __name__)

# Setup logging
logging.basicConfig(
    filename="logs/feedback_routes.log",  # Store logs in a dedicated directory
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@feedback_bp.route("/predict-only", methods=["POST"])
def predict_only():
    """
    Predicts URL and stores result (no feedback).
    """
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        prediction = predict_url(url)
        label = "phishing" if prediction == 1 else "safe"
        doc_id = insert_prediction(url, label)

        logging.info(f" Predict-only: {url} → {label} | ID: {doc_id}")
        return jsonify({
            "url": url,
            "result": label,
            "id": str(doc_id)
        }), 200
    except Exception as e:
        logging.error(f" Prediction-only failed: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@feedback_bp.route("/predict-feedback", methods=["POST"])
def predict_with_feedback():
    """
    Predicts URL and stores both prediction and user feedback.
    """
    data = request.get_json()
    url = data.get("url")
    feedback = data.get("feedback")

    if not url or not feedback:
        return jsonify({"error": "Missing URL or feedback"}), 400

    try:
        prediction = predict_url(url)
        label = "phishing" if prediction == 1 else "safe"
        doc_id = insert_prediction(url, label)
        updated = update_feedback(str(doc_id), feedback)

        logging.info(f" Predict+Feedback: {url} → {label} | Feedback: {feedback} | ID: {doc_id}")
        return jsonify({
            "url": url,
            "result": label,
            "id": str(doc_id),
            "feedback": feedback,
            "feedback_updated": updated
        }), 200
    except Exception as e:
        logging.error(f" Prediction with feedback failed: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@feedback_bp.route("/feedback/<record_id>", methods=["PUT"])
def add_feedback(record_id):
    """
    Updates feedback for a prediction record by ID.
    """
    data = request.get_json()
    feedback = data.get("feedback")

    if not feedback:
        return jsonify({"error": "Missing feedback"}), 400

    try:
        success = update_feedback(record_id, feedback)
        if success:
            logging.info(f"Feedback updated | ID: {record_id} | Feedback: {feedback}")
            return jsonify({"message": "Feedback updated successfully"}), 200
        else:
            logging.warning(f" Feedback update failed | ID: {record_id}")
            return jsonify({"error": "Record not found or feedback unchanged"}), 404
    except Exception as e:
        logging.error(f" Feedback update error: {str(e)}")
        return jsonify({"error": f"Update failed: {str(e)}"}), 500

@feedback_bp.route("/records", methods=["GET"])
def get_all_records():
    """
    Returns all prediction records from the database.
    """
    try:
        records = get_all_predictions()
        for record in records:
            record["_id"] = str(record["_id"])

        logging.info(f" Retrieved all records: {len(records)} found")
        return jsonify(records), 200
    except Exception as e:
        logging.error(f"Failed to fetch records: {str(e)}")
        return jsonify({"error": f"Failed to fetch records: {str(e)}"}), 500

@feedback_bp.route("/record/<record_id>", methods=["GET"])
def get_record_by_id(record_id):
    """
    Fetches a specific prediction record by ID.
    """
    try:
        record = get_prediction_by_id(record_id)
        if record:
            record["_id"] = str(record["_id"])
            logging.info(f"Record retrieved | ID: {record_id}")
            return jsonify(record), 200
        else:
            logging.warning(f"Record not found | ID: {record_id}")
            return jsonify({"error": "Record not found"}), 404
    except Exception as e:
        logging.error(f" Error fetching record {record_id}: {str(e)}")
        return jsonify({"error": f"Failed to fetch record: {str(e)}"}), 500
