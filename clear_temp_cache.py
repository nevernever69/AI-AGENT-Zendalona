import asyncio
import logging
from config import settings
from utils.mongo_utils import get_temp_cache_collection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_temp_cache():
    """Clear all temporary cache entries"""
    try:
        collection = get_temp_cache_collection()
        result = await collection.delete_many({})
        logger.info(f"Deleted {result.deleted_count} temporary cache entries")
        print(f"Successfully cleared {result.deleted_count} temporary cache entries")
    except Exception as e:
        logger.error(f"Error clearing temp cache: {str(e)}")
        print(f"Error clearing temp cache: {str(e)}")

if __name__ == "__main__":
    asyncio.run(clear_temp_cache())