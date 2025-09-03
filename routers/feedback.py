from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.mongo_utils import get_all_feedback, delete_feedback, update_and_move_feedback_to_cache

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackItem(BaseModel):
    question: str
    answer: str

@router.get("/", summary="Get all feedback items")
async def get_feedback():
    """Retrieve all feedback items from the database."""
    try:
        items = await get_all_feedback()
        processed_items = []
        for item in items:
            item['_id'] = str(item['_id'])
            # Map 'query' to 'question' and 'response' to 'answer'
            # Also include the 'feedback' field
            processed_items.append({
                "question": item.get("query"),
                "answer": item.get("response"),
                "feedback": item.get("feedback"),
                "additional_comments": item.get("additional_comments"),
                "timestamp": item.get("timestamp"),
                "user_id": item.get("user_id"),
                "user_email": item.get("user_email"),
                "user_name": item.get("user_name"),
                "_id": item.get("_id")
            })
        return processed_items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}", summary="Delete a feedback item")
async def delete_feedback_item(item_id: str):
    """Delete a specific feedback item from the database."""
    try:
        success = await delete_feedback(item_id)
        if success:
            return {"message": f"Feedback item {item_id} deleted."}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/move-to-cache/{item_id}", summary="Update and move feedback to cache")
async def move_feedback_to_cache(item_id: str, item: FeedbackItem):
    """Update a feedback item and move it to the permanent cache."""
    try:
        success = await update_and_move_feedback_to_cache(item_id, item.question, item.answer)
        if success:
            return {"message": f"Feedback item {item_id} updated and moved to permanent cache."}
        else:
            raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))