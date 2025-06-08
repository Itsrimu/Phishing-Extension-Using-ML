from flask import Blueprint, request, jsonify, current_app
import logging

from predict import load_model, predict_url
from database import (
    insert_prediction,
    insert_reported_phishing,
    get_prediction_by_id,
    get_all_predictions
)

# Blueprint for prediction routes
prediction_bp = Blueprint('prediction_bp', __name__)

# Load model once at startup
try:
    model = load_model()
    logging.info("Model loaded successfully.")
except Exception as e:
    model = None
    logging.error(f"Model load error: {e}")

# ----------------- Internal Helper ------------------

def predict_url_logic(url: str) -> dict:
    result = predict_url(url)
    return {
        "analysis_result": result.get("analysis_result", "unknown")
    }

# ----------------- ROUTES ------------------

@prediction_bp.route("/predict", methods=["POST"], strict_slashes=False)
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        if not url:
            return jsonify({"error": "Missing 'url' field"}), 400

        result = predict_url_logic(url)
        prediction_record = insert_prediction(url, result["analysis_result"], None)
        record_id = str(prediction_record.get("id")) if prediction_record else None

        return jsonify({
            "url": url,
            "analysis_result": result["analysis_result"],
            "record_id": record_id
        }), 200

    except Exception as e:
        logging.exception("Error in /predict")
        return jsonify({"error": str(e)}), 500

@prediction_bp.route("/predict-only", methods=["POST"], strict_slashes=False)
def predict_only():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        if not url:
            return jsonify({"error": "Missing 'url' field"}), 400

        result = predict_url_logic(url)
        return jsonify(result), 200

    except Exception as e:
        logging.exception("Error in /predict-only")
        return jsonify({"error": str(e)}), 500

@prediction_bp.route("/report", methods=["POST"], strict_slashes=False)
def report_phishing():
    try:
        data = request.get_json(force=True)
        url = data.get("url")
        reason = data.get("reason", "User reported phishing")

        if not url:
            return jsonify({"error": "Missing 'url' field"}), 400

        response = insert_reported_phishing(url, reason)
        report_id = str(response.get("id")) if response else None

        return jsonify({
            "status": "success",
            "url": url,
            "reason": reason,
            "id": report_id
        }), 200

    except Exception as e:
        logging.exception("Error in /report")
        return jsonify({"error": f"Failed to store report: {str(e)}"}), 500

@prediction_bp.route("/record/<record_id>", methods=["GET"], strict_slashes=False)
def get_prediction(record_id):
    try:
        record = get_prediction_by_id(record_id)
        if record:
            record["id"] = str(record.pop("_id", record_id))
            return jsonify(record), 200
        else:
            return jsonify({"error": "Record not found"}), 404
    except Exception as e:
        logging.exception("Error in /record/<record_id>")
        return jsonify({"error": f"Failed to fetch record: {str(e)}"}), 500

@prediction_bp.route("/records", methods=["GET"], strict_slashes=False)
def get_all_prediction_records():
    try:
        records = get_all_predictions()
        for record in records:
            record["id"] = str(record.pop("_id", ""))
        return jsonify(records), 200
    except Exception as e:
        logging.exception("Error in /records")
        return jsonify({"error": f"Failed to fetch records: {str(e)}"}), 500

@prediction_bp.route("/batch-predict", methods=["POST"], strict_slashes=False)
def batch_predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        data = request.get_json(force=True)
        urls = data.get("urls")
        if not urls or not isinstance(urls, list):
            return jsonify({"error": "Invalid 'urls' field. Must be a list of URLs."}), 400

        results = []
        for url in urls:
            try:
                result = predict_url_logic(url)
                doc = insert_prediction(url, result["analysis_result"], None)
                doc_id = str(doc.get("id")) if doc else None
                results.append({
                    "id": doc_id,
                    "url": url,
                    "analysis_result": result["analysis_result"]
                })
            except Exception as e:
                results.append({"url": url, "error": str(e)})

        return jsonify(results), 200

    except Exception as e:
        logging.exception("Error in /batch-predict")
        return jsonify({"error": str(e)}), 500

@prediction_bp.route("/batch", methods=["POST"], strict_slashes=False)
def batch_simple_predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
    try:
        data = request.get_json(force=True)
        urls = data.get("urls")
        if not urls or not isinstance(urls, list):
            return jsonify({"error": "Invalid 'urls' field. Must be a list."}), 400

        results = {}
        for url in urls:
            try:
                result = predict_url_logic(url)
                results[url] = {
                    "analysis_result": result["analysis_result"]
                }
            except Exception as e:
                results[url] = {"error": str(e)}

        return jsonify(results), 200

    except Exception as e:
        logging.exception("Error in /batch")
        return jsonify({"error": str(e)}), 500
