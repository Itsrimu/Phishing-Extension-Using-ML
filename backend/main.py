from flask import Flask, jsonify
from flask_cors import CORS
from routes.feedback_routes import feedback_bp
from routes.predict_routes import prediction_bp
import logging
import os
import sys

# ------------------- Setup Logging -------------------

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# ------------------- Initialize Flask -------------------

app = Flask(__name__)

# Allow all origins for development; restrict in production!
CORS(app)  # For production: CORS(app, origins=["https://your-frontend-domain.com"])

# ------------------- Register Routes -------------------

# Prediction logic under /api/*
app.register_blueprint(prediction_bp, url_prefix="/api")

# Feedback-related routes under /api/feedback/*
app.register_blueprint(feedback_bp, url_prefix="/api/feedback")

# ------------------- Health Check -------------------

@app.route("/", methods=["GET"])
def home():
    logging.info("Health check passed.")
    return jsonify({"message": "Phishing URL Detection API is up and running!"}), 200

# ------------------- Global Error Handler -------------------

@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("Unhandled exception occurred:")
    # In development, you can return the actual error message:
    # return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Internal Server Error"}), 500

# ------------------- Start Server -------------------

if __name__ == "__main__":
    logging.info("Starting Flask server at http://127.0.0.1:5000")
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
