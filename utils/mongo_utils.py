import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mongo_client():
    """Initialize and return a MongoDB client."""
    try:
        client = AsyncIOMotorClient(settings.mongodb_uri)
        return client
    except Exception as e:
        logger.error(f"Error initializing MongoDB client: {str(e)}")
        raise

def get_feedback_collection():
    """Get the feedback collection from MongoDB."""
    try:
        client = get_mongo_client()
        db = client[settings.mongodb_database]
        collection = db[settings.mongodb_feedback_collection]
        return collection
    except Exception as e:
        logger.error(f"Error accessing feedback collection: {str(e)}")
        raise

async def save_feedback(feedback_data: dict) -> bool:
    """Save feedback data to MongoDB."""
    try:
        collection = get_feedback_collection()
        result = await collection.insert_one(feedback_data)
        logger.info(f"Saved feedback with ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return False