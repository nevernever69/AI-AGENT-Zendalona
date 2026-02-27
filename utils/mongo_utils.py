async def save_chat(session_id, user_msg, bot_msg):
    collection = db.chat_history
    await collection.insert_one({
        "session_id": session_id,
        "user": user_msg,
        "bot": bot_msg
    })

async def get_chat_history(session_id, limit=5):
    collection = db.chat_history
    chats = collection.find({"session_id": session_id}).sort("_id", -1).limit(limit)
    return [chat async for chat in chats]