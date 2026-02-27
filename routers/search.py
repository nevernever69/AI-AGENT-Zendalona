from fastapi import APIRouter
from utils.mongo_utils import db

router = APIRouter()

@router.get("/chat/search")
async def search_chat(query: str):
    """
    Search keyword in chat history (user + bot messages)
    """

    collection = db.chat_history

    results = collection.find({
        "$or": [
            {"user": {"$regex": query, "$options": "i"}},
            {"bot": {"$regex": query, "$options": "i"}}
        ]
    })

    data = []
    async for chat in results:
        data.append({
            "user": chat.get("user"),
            "bot": chat.get("bot"),
            "session_id": chat.get("session_id")
        })

    return {
        "query": query,
        "results": data
    }