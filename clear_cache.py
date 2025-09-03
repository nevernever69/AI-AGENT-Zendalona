import logging
from config import settings
from utils.chroma_utils import get_chroma_db

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_COLLECTION_NAME = "zendalona_cache"

def clear_cache():
    """Clear all cached entries"""
    try:
        db = get_chroma_db(collection_name=CACHE_COLLECTION_NAME)
        # Get all document IDs
        all_docs = db.get()
        if all_docs and all_docs["ids"]:
            # Delete all documents
            db.delete(ids=all_docs["ids"])
            logger.info(f"Deleted {len(all_docs['ids'])} cached entries")
            print(f"Successfully cleared {len(all_docs['ids'])} cached entries")
        else:
            print("Cache is already empty")
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        print(f"Error clearing cache: {str(e)}")

if __name__ == "__main__":
    clear_cache()