import os
from bson import ObjectId
from pymongo import MongoClient, errors
from dotenv import load_dotenv
from typing import Optional, Dict, List, Union

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
REPORTED_COLLECTION_NAME = os.getenv("REPORTED_COLLECTION_NAME", "reported_phishing")

if not MONGO_URI or not DB_NAME or not COLLECTION_NAME:
    raise EnvironmentError("Missing required MongoDB environment variables.")

# MongoDB Connection
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    reported_collection = db[REPORTED_COLLECTION_NAME]
    client.server_info()  # Force connection on a request as the connect=True parameter of MongoClient seems unreliable.
except errors.ServerSelectionTimeoutError as e:
    raise ConnectionError(f"Could not connect to MongoDB: {e}")

# -------------------- Prediction Storage --------------------

def insert_prediction(url: str, prediction: str, confidence: Optional[float] = None) -> Dict[str, Union[bool, str]]:
    doc = {
        "url": url.strip(),
        "prediction": prediction.lower().strip(),
        "confidence": confidence,
        "feedback": None
    }
    try:
        result = collection.insert_one(doc)
        return {"success": True, "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error inserting prediction: {e}")
        return {"success": False, "id": ""}

def update_feedback(record_id: str, feedback: str) -> bool:
    if not ObjectId.is_valid(record_id):
        return False
    try:
        result = collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": {"feedback": feedback.lower().strip()}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error updating feedback: {e}")
        return False

def get_prediction_by_id(record_id: str) -> Optional[Dict]:
    if not ObjectId.is_valid(record_id):
        return None
    try:
        doc = collection.find_one({"_id": ObjectId(record_id)})
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    except Exception as e:
        print(f"Error fetching prediction by ID: {e}")
        return None

def get_all_predictions() -> List[Dict]:
    try:
        docs = list(collection.find())
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return docs
    except Exception as e:
        print(f"Error fetching all predictions: {e}")
        return []

def delete_prediction_by_id(record_id: str) -> bool:
    if not ObjectId.is_valid(record_id):
        return False
    try:
        result = collection.delete_one({"_id": ObjectId(record_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return False

# -------------------- Reported Phishing Storage --------------------

def insert_reported_phishing(url: str, reason: str) -> Dict[str, Union[bool, str]]:
    doc = {
        "url": url.strip(),
        "reported_by_user": True,
        "reason": reason.strip(),
        "used_for_training": False
    }
    try:
        result = reported_collection.insert_one(doc)
        return {"success": True, "id": str(result.inserted_id)}
    except Exception as e:
        print(f"Error inserting reported phishing: {e}")
        return {"success": False, "id": ""}

def get_reported_phishing_urls() -> List[Dict]:
    try:
        docs = list(reported_collection.find({"used_for_training": False}))
        for doc in docs:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        return docs
    except Exception as e:
        print(f"Error fetching reported phishing URLs: {e}")
        return []

def mark_as_trained(url: str) -> bool:
    try:
        result = reported_collection.update_one(
            {"url": url.strip()},
            {"$set": {"used_for_training": True}}
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"Error marking as trained: {e}")
        return False
