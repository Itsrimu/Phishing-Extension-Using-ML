from flask import Blueprint, request, jsonify
from database import insert_prediction, update_feedback, get_all_predictions, get_prediction_by_id
from predict import predict_url
import logging

feedback_bp = Blueprint('feedback', __name__)

# Setup logging
logging.basicConfig(
    filename="logs/feedback_routes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_request(action, url=None, record_id=None, feedback=None, error=None):
    """Structured logging for request actions."""
    message = f"{action} | URL: {url}" if url else f"{action} | ID: {record_id}"
    if feedback:
        message += f" | Feedback: {feedback}"
    if error:
        message += f" | Error: {error}"
        logging.error(message)
    else:
        logging.info(message)

@feedback_bp.route("/predict-only", methods=["POST"])
def predict_only():
    """Predicts a URL and stores result without feedback."""
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "Missing URL"}), 400

    try:
        label = predict_url(url)  # Calls the `predict_url` function
        doc_id = insert_prediction(url, label.lower())  # Ensure consistent lowercase labels

        log_request("Predict-only", url=url, record_id=doc_id)
        
        return jsonify({
            "url": url,
            "result": label,
            "id": str(doc_id)
        }), 200

    except Exception as e:
        log_request("Predict-only Failed", url=url, error=str(e))
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@feedback_bp.route("/predict-feedback", methods=["POST"])
def predict_with_feedback():
    """Predicts a URL, stores the result, and updates user feedback."""
    data = request.get_json()
    url, feedback = data.get("url"), data.get("feedback")

    if not url or not feedback:
        return jsonify({"error": "Missing URL or feedback"}), 400

    try:
        label = predict_url(url)
        doc_id = insert_prediction(url, label.lower())  # Store label consistently
        updated = update_feedback(str(doc_id), feedback)

        log_request("Predict+Feedback", url=url, record_id=doc_id, feedback=feedback)
        
        return jsonify({
            "url": url,
            "result": label,
            "id": str(doc_id),
            "feedback": feedback,
            "feedback_updated": updated
        }), 200

    except Exception as e:
        log_request("Predict+Feedback Failed", url=url, feedback=feedback, error=str(e))
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

@feedback_bp.route("/feedback/<record_id>", methods=["PUT"])
def add_feedback(record_id):
    """Updates feedback for a stored prediction record."""
    data = request.get_json()
    feedback = data.get("feedback")

    if not feedback:
        return jsonify({"error": "Missing feedback"}), 400

    try:
        success = update_feedback(record_id, feedback)
        if success:
            log_request("Feedback updated", record_id=record_id, feedback=feedback)
            return jsonify({"message": "Feedback updated successfully"}), 200
        else:
            log_request("Feedback update failed", record_id=record_id)
            return jsonify({"error": "Record not found or feedback unchanged"}), 404

    except Exception as e:
        log_request("Feedback update error", record_id=record_id, error=str(e))
        return jsonify({"error": f"Update failed: {str(e)}"}), 500

@feedback_bp.route("/records", methods=["GET"])
def get_all_records():
    """Retrieves all prediction records from the database."""
    try:
        records = get_all_predictions()
        for record in records:
            record["_id"] = str(record["_id"])  # Ensure proper serialization

        log_request("Retrieved all records", record_id=len(records))
        return jsonify(records), 200

    except Exception as e:
        log_request("Failed to fetch records", error=str(e))
        return jsonify({"error": f"Failed to fetch records: {str(e)}"}), 500

@feedback_bp.route("/record/<record_id>", methods=["GET"])
def get_record_by_id(record_id):
    """Fetches a specific prediction record by ID."""
    try:
        record = get_prediction_by_id(record_id)
        if record:
            record["_id"] = str(record["_id"])  # Ensure proper serialization
            log_request("Record retrieved", record_id=record_id)
            return jsonify(record), 200
        else:
            log_request("Record not found", record_id=record_id)
            return jsonify({"error": "Record not found"}), 404

    except Exception as e:
        log_request("Error fetching record", record_id=record_id, error=str(e))
        return jsonify({"error": f"Failed to fetch record: {str(e)}"}), 500
