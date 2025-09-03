import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from functools import lru_cache

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)
logger = logging.getLogger(__name__)

@lru_cache(maxsize=None)
def get_mongo_client():
    """Initialize and return a memoized MongoDB client."""
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

def get_temp_cache_collection():
    """Get the temporary cache collection from MongoDB and ensure TTL index."""
    try:
        client = get_mongo_client()
        db = client[settings.mongodb_database]
        collection = db["temp_cache"]
        # Create a TTL index on the 'createdAt' field to automatically delete documents after 8 days (691200 seconds)
        collection.create_index("createdAt", expireAfterSeconds=691200)
        return collection
    except Exception as e:
        logger.error(f"Error accessing temporary cache collection: {str(e)}")
        raise

async def save_to_temp_cache(question: str, answer: str, sources: list, source: str = "gemini") -> bool:
    """Save a Q&A pair to the temporary cache."""
    try:
        collection = get_temp_cache_collection()
        from datetime import datetime, timezone
        await collection.insert_one({
            "question": question,
            "answer": answer,
            "sources": sources,
            "source": source,  # Add source information
            "createdAt": datetime.now(timezone.utc)
        })
        logger.info(f"Saved to temporary cache: '{question[:50]}...' from {source}")
        return True
    except Exception as e:
        logger.error(f"Error saving to temporary cache: {str(e)}")
        return False

async def get_all_temp_cache() -> list:
    """Retrieve all Q&A pairs from the temporary cache."""
    try:
        collection = get_temp_cache_collection()
        cursor = collection.find({})
        return await cursor.to_list(length=None)
    except Exception as e:
        logger.error(f"Error retrieving from temporary cache: {str(e)}")
        return []

async def move_to_permanent_cache(item_id: str) -> bool:
    """Move an item from temporary cache to permanent cache and delete it from temporary."""
    try:
        temp_collection = get_temp_cache_collection()
        from bson.objectid import ObjectId
        item = await temp_collection.find_one({"_id": ObjectId(item_id)})
        if not item:
            return False
        
        from utils.cache_utils import add_to_cache
        add_to_cache(item['question'], item['answer'], source="from_temp_cache")
        
        await temp_collection.delete_one({"_id": ObjectId(item_id)})
        logger.info(f"Moved item {item_id} to permanent cache.")
        return True
    except Exception as e:
        logger.error(f"Error moving item {item_id} to permanent cache: {str(e)}")
        return False

async def update_in_temp_cache(item_id: str, question: str, answer: str) -> bool:
    """Update an item in the temporary cache."""
    try:
        temp_collection = get_temp_cache_collection()
        from bson.objectid import ObjectId
        result = await temp_collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": {"question": question, "answer": answer}}
        )
        if result.modified_count > 0:
            logger.info(f"Updated item {item_id} in temporary cache.")
            return True
        return False
    except Exception as e:
        logger.error(f"Error updating item {item_id} in temporary cache: {str(e)}")
        return False

async def update_and_move_to_permanent_cache(item_id: str, question: str, answer: str) -> bool:
    """Update an item in the temporary cache and move it to the permanent cache."""
    try:
        temp_collection = get_temp_cache_collection()
        from bson.objectid import ObjectId

        # First, add the updated item to the permanent cache
        from utils.cache_utils import add_to_cache
        add_to_cache(question, answer, source="from_temp_cache_edited")

        # Then, delete the original item from the temporary cache
        await temp_collection.delete_one({"_id": ObjectId(item_id)})
        
        logger.info(f"Updated and moved item {item_id} to permanent cache.")
        return True
    except Exception as e:
        logger.error(f"Error updating and moving item {item_id} to permanent cache: {str(e)}")
        return False

async def delete_from_temp_cache(item_id: str) -> bool:
    """Delete an item from the temporary cache."""
    try:
        temp_collection = get_temp_cache_collection()
        from bson.objectid import ObjectId
        result = await temp_collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count > 0:
            logger.info(f"Deleted item {item_id} from temporary cache.")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting item {item_id} from temporary cache: {str(e)}")
        return False

async def get_all_feedback() -> list:
    """Retrieve all feedback items from the database."""
    try:
        collection = get_feedback_collection()
        cursor = collection.find({})
        return await cursor.to_list(length=None)
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        return []

async def delete_feedback(item_id: str) -> bool:
    """Delete a feedback item from the database."""
    try:
        collection = get_feedback_collection()
        from bson.objectid import ObjectId
        result = await collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count > 0:
            logger.info(f"Deleted feedback item {item_id}.")
            return True
        return False
    except Exception as e:
        logger.error(f"Error deleting feedback item {item_id}: {str(e)}")
        return False

async def update_and_move_feedback_to_cache(item_id: str, question: str, answer: str) -> bool:
    """Update a feedback item and move it to the permanent cache."""
    try:
        collection = get_feedback_collection()
        from bson.objectid import ObjectId
        from utils.cache_utils import add_to_cache
        add_to_cache(question, answer, source="from_feedback")
        await collection.delete_one({"_id": ObjectId(item_id)})
        logger.info(f"Moved feedback item {item_id} to permanent cache.")
        return True
    except Exception as e:
        logger.error(f"Error moving feedback item {item_id} to permanent cache: {str(e)}")
        return False

async def clear_temp_cache() -> bool:
    """Clear all items from the temporary cache collection."""
    try:
        collection = get_temp_cache_collection()
        result = await collection.delete_many({})
        logger.info(f"Cleared temporary cache. Deleted {result.deleted_count} items.")
        return True
    except Exception as e:
        logger.error(f"Error clearing temporary cache: {str(e)}")
        return False