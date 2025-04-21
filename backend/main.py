from flask import Flask, jsonify
from flask_cors import CORS
from routes.feedback_routes import feedback_bp
# from routes.predict_routes import predict_bp  # Uncomment if you have this too

import logging
import os

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Setup application-level logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS if you plan to call from frontend

# Register Blueprints
app.register_blueprint(feedback_bp, url_prefix="/api/feedback")
# app.register_blueprint(predict_bp, url_prefix="/api/predict")  # Uncomment when needed

# Health Check Endpoint
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": " Phishing URL Detection API is up and running!"}), 200

# Global Error Handler (Optional)
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {str(e)}")
    return jsonify({"error": "Internal Server Error"}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
