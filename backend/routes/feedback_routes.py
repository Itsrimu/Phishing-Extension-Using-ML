from flask import Blueprint, request, jsonify
from pathlib import Path
import logging

from predict import predict_url, load_model
from database import (
    insert_prediction,
    update_feedback,
    get_all_predictions,
    get_prediction_by_id,
    insert_reported_phishing
)

feedback_bp = Blueprint("feedback", __name__)
MODEL_PATH = Path("model/phishing_rf_model.pkl")

# Load model at startup
try:
    model = load_model(MODEL_PATH)
    logging.info("Model loaded successfully.")
except Exception as e:
    model = None
    logging.error(f"Failed to load model: {e}")

# -------------------- Utility Function --------------------

def run_prediction_and_store(url: str):
    if model is None:
        raise Exception("Model not loaded")

    result = predict_url(model, url)
    label = result.get("analysis_result", "unknown")
    doc_id = insert_prediction(url, label, None)
    return doc_id, label

# -------------------- Predict Only --------------------

@feedback_bp.route("/predict-only", methods=["POST"], strict_slashes=False)
def predict_only():
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        if not url:
            return jsonify({"error": "Missing 'url' field"}), 400

        doc_id, label = run_prediction_and_store(url)
        return jsonify({
            "id": str(doc_id),
            "url": url,
            "analysis_result": label
        }), 200

    except Exception as e:
        logging.exception("Error in /predict-only")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

# -------------------- Submit Feedback --------------------

@feedback_bp.route("/feedback", methods=["POST"], strict_slashes=False)
def feedback():
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        feedback_val = data.get("feedback")

        if not url or not feedback_val:
            return jsonify({"error": "Missing 'url' or 'feedback' field"}), 400

        doc_id, label = run_prediction_and_store(url)
        updated = update_feedback(str(doc_id), feedback_val)
        return jsonify({
            "id": str(doc_id),
            "url": url,
            "analysis_result": label,
            "feedback": feedback_val,
            "feedback_updated": updated
        }), 200

    except Exception as e:
        logging.exception("Error in /feedback")
        return jsonify({"error": f"Feedback submission failed: {str(e)}"}), 500

# -------------------- Predict and Submit Feedback --------------------

@feedback_bp.route("/predict-feedback", methods=["POST"], strict_slashes=False)
def predict_with_feedback():
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        feedback_val = data.get("feedback")

        if not url or not feedback_val:
            return jsonify({"error": "Missing 'url' or 'feedback' field"}), 400

        doc_id, label = run_prediction_and_store(url)
        updated = update_feedback(str(doc_id), feedback_val)
        return jsonify({
            "id": str(doc_id),
            "url": url,
            "analysis_result": label,
            "feedback": feedback_val,
            "feedback_updated": updated
        }), 200

    except Exception as e:
        logging.exception("Error in /predict-feedback")
        return jsonify({"error": f"Prediction and feedback failed: {str(e)}"}), 500

# -------------------- Update Feedback by Record ID --------------------

@feedback_bp.route("/feedback/<record_id>", methods=["PUT"], strict_slashes=False)
def add_feedback(record_id: str):
    try:
        data = request.get_json(force=True)
        feedback_val = data.get("feedback")

        if not feedback_val:
            return jsonify({"error": "Missing 'feedback' field"}), 400

        updated = update_feedback(record_id, feedback_val)
        if updated:
            return jsonify({"message": "Feedback updated successfully"}), 200
        else:
            return jsonify({"error": "Record not found or feedback unchanged"}), 404

    except Exception as e:
        logging.exception("Error in /feedback/<record_id>")
        return jsonify({"error": f"Failed to update feedback: {str(e)}"}), 500

# -------------------- Get All Prediction Records --------------------

@feedback_bp.route("/records", methods=["GET"], strict_slashes=False)
def get_all_records():
    try:
        records = get_all_predictions()
        for record in records:
            record["_id"] = str(record["_id"])
        return jsonify(records), 200

    except Exception as e:
        logging.exception("Error in /records")
        return jsonify({"error": f"Failed to fetch records: {str(e)}"}), 500

# -------------------- Get Single Record --------------------

@feedback_bp.route("/record/<record_id>", methods=["GET"], strict_slashes=False)
def get_record_by_id(record_id: str):
    try:
        record = get_prediction_by_id(record_id)
        if record:
            record["_id"] = str(record["_id"])
            return jsonify(record), 200
        else:
            return jsonify({"error": "Record not found"}), 404

    except Exception as e:
        logging.exception("Error in /record/<record_id>")
        return jsonify({"error": f"Failed to fetch record: {str(e)}"}), 500

# -------------------- Report Phishing URL --------------------

@feedback_bp.route("/report", methods=["POST"], strict_slashes=False)
def report_phishing():
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        reason = data.get("reason", "User reported phishing")

        if not url:
            return jsonify({"error": "Missing 'url' field"}), 400

        result = insert_reported_phishing(url, reason)
        return jsonify({
            "status": "success" if result["success"] else "error",
            "id": result["id"],
            "url": url,
            "reason": reason
        }), 200 if result["success"] else 500

    except Exception as e:
        logging.exception("Error in /report")
        return jsonify({"error": f"Failed to report URL: {str(e)}"}), 500
