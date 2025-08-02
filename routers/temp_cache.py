from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.mongo_utils import get_all_temp_cache, move_to_permanent_cache, update_and_move_to_permanent_cache, delete_from_temp_cache, update_in_temp_cache

router = APIRouter(prefix="/temp-cache", tags=["Temporary Cache"])

class TempCacheItem(BaseModel):
    question: str
    answer: str

@router.get("/", summary="Get all temporary cache items")
async def get_temp_cache():
    """Retrieve all question-answer pairs from the temporary cache."""
    try:
        items = await get_all_temp_cache()
        # Convert ObjectId to string for JSON serialization
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{item_id}", summary="Update a temporary cache item")
async def update_item_in_temp_cache(item_id: str, item: TempCacheItem):
    """Update a specific Q&A pair in the temporary cache."""
    try:
        success = await update_in_temp_cache(item_id, item.question, item.answer)
        if success:
            return {"message": f"Item {item_id} updated successfully."}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/move/{item_id}", summary="Move item to permanent cache")
async def move_item_to_permanent_cache(item_id: str):
    """Move a specific Q&A pair from the temporary cache to the permanent cache."""
    try:
        success = await move_to_permanent_cache(item_id)
        if success:
            return {"message": f"Item {item_id} moved to permanent cache."}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update-and-move/{item_id}", summary="Update item and move to permanent cache")
async def update_and_move_item(item_id: str, item: TempCacheItem):
    """Update a Q&A pair and move it from the temporary cache to the permanent cache."""
    try:
        success = await update_and_move_to_permanent_cache(item_id, item.question, item.answer)
        if success:
            return {"message": f"Item {item_id} updated and moved to permanent cache."}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}", summary="Delete item from temporary cache")
async def delete_item_from_temp_cache(item_id: str):
    """Delete a specific Q&A pair from the temporary cache."""
    try:
        success = await delete_from_temp_cache(item_id)
        if success:
            return {"message": f"Item {item_id} deleted from temporary cache."}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
