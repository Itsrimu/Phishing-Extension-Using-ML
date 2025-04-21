import os
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Establish MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def insert_prediction(url, prediction):
    """
    Insert a new prediction document into the database.
    
    :param url: The URL being evaluated.
    :param prediction: Result of the prediction ('phishing' or 'safe').
    :return: The inserted document's ObjectId.
    """
    doc = {
        "url": url,
        "prediction": prediction,
        "feedback": None
    }
    result = collection.insert_one(doc)
    return result.inserted_id


def update_feedback(record_id, feedback):
    """
    Update feedback for an existing prediction document.
    
    :param record_id: The string form of MongoDB ObjectId.
    :param feedback: Feedback string (e.g., "correct", "incorrect").
    :return: True if the update was successful, False otherwise.
    """
    result = collection.update_one(
        {"_id": ObjectId(record_id)},
        {"$set": {"feedback": feedback}}
    )
    return result.modified_count > 0


def get_prediction_by_id(record_id):
    """
    Retrieve a single prediction document by ID.
    
    :param record_id: The string form of MongoDB ObjectId.
    :return: The document as a dictionary, or None if not found.
    """
    return collection.find_one({"_id": ObjectId(record_id)})


def get_all_predictions():
    """
    Retrieve all prediction documents from the database.
    
    :return: List of all prediction documents.
    """
    return list(collection.find())


def delete_prediction_by_id(record_id):
    """
    Delete a prediction document by ID.
    
    :param record_id: The string form of MongoDB ObjectId.
    :return: True if a document was deleted, False otherwise.
    """
    result = collection.delete_one({"_id": ObjectId(record_id)})
    return result.deleted_count > 0
