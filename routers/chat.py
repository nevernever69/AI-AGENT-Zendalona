import json
import logging
from fastapi import APIRouter, HTTPException, Depends, Body, WebSocket
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any, AsyncGenerator, Optional, List
from utils.models import ChatRequest, ChatResponse, StreamingChatRequest, FeedbackRequest
from utils.langchain_utils import get_rag_chain, process_query, get_streaming_chain, generate_suggestions
from utils.cache_utils import get_from_cache, cache_chatbot_response
from utils.mongo_utils import save_feedback, save_to_temp_cache
import asyncio
import uuid
import time

router = APIRouter(prefix="/chat", tags=["Chat"])

# Track active chat sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

from utils.chroma_utils import get_chroma_db

@router.post(
    "",
    response_model=ChatResponse,
    summary="Get a complete chat response",
    description="Process a chat query and return a complete response with sources",
    response_description="A chat response with answer and sources",
)
async def chat(request: ChatRequest):
    """
    Process a chat query and return a complete response with sources.
    
    - **query**: The user's question or message
    - **session_id**: Optional unique identifier for the chat session
    """
    try:
        cached_results = get_from_cache(request.query)
        
        if cached_results:
            top_hit, score = cached_results[0]
            similarity = 1.0 - score
            # Use a more lenient threshold for short queries (like greetings)
            threshold = 0.99 if len(request.query) > 10 else 0.85
            if similarity >= threshold:
                answer = top_hit.metadata.get("answer", "")
                sources = [f"[CACHED - {top_hit.metadata.get('source', 'unknown')} - similarity: {similarity:.2f}]"]
                suggestions = await generate_suggestions(request.query, answer)
                # Save to temporary cache with source information
                await save_to_temp_cache(request.query, answer, sources, source="cache")
                return ChatResponse(response=answer, sources=sources, suggestions=suggestions, feedback_enabled=True)

        chain = get_rag_chain()
        response, sources = process_query(chain, request.query)
        logging.info(f"Processed query with Gemini: {request.query}")
        
        suggestions = await generate_suggestions(request.query, response)
        
        # Save to temporary cache with source information
        await save_to_temp_cache(request.query, response, sources, source="gemini")
        
        return ChatResponse(response=response, sources=sources, suggestions=suggestions, feedback_enabled=True)
    except Exception as e:
        logging.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def stream_response(query: str, session_id: str) -> AsyncGenerator[dict, None]:
    """Generate a streaming response for the chat query."""
    try:
        # Use the streaming chain for all responses to ensure consistency
        chain, retriever = get_streaming_chain()
        
        # Check cache first with dynamic threshold based on query length
        cached_results = get_from_cache(query)
        if cached_results:
            top_hit, score = cached_results[0]
            similarity = 1.0 - score
            # Use a more lenient threshold for short queries (like greetings)
            threshold = 0.60 if len(query) > 10 else 0.50
            if similarity >= threshold:
                logging.info(f"Streaming cached response for query: {query}")
                answer = top_hit.metadata.get("answer", "")
                sources = [f"[CACHED - {top_hit.metadata.get('source', 'unknown')} - similarity: {similarity:.2f}]"]
                suggestions = await generate_suggestions(query, answer)

                # Stream the cached answer word by word
                words = answer.split()
                for word in words:
                    yield {"event": "message", "data": f"{word} "}
                    await asyncio.sleep(0.05)
                
                yield {"event": "sources", "data": ",".join(sources)}
                yield {"event": "suggestions", "data": "|".join(suggestions)}
                yield {"event": "metadata", "data": json.dumps({"feedback_enabled": True})}
                yield {"event": "done", "data": ""}
                
                # Save to temporary cache with source information
                await save_to_temp_cache(query, answer, sources, source="cache")
                return

        # If not in cache, proceed with the streaming chain
        if session_id not in active_sessions:
            active_sessions[session_id] = {"created_at": time.time(), "queries": []}
        active_sessions[session_id]["queries"].append(query)
        active_sessions[session_id]["last_active"] = time.time()

        docs = retriever.get_relevant_documents(query)
        sources = [doc.metadata.get("source", "") for doc in docs if doc.metadata.get("source")]
        context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""

        full_response = []

        async for chunk in chain.astream({"context": context, "question": query}):
            content = chunk.content if hasattr(chunk, "content") else str(chunk)
            full_response.append(content)
            yield {"event": "message", "data": content}
            await asyncio.sleep(0.01)

        final_response = "".join(full_response)
        suggestions = await generate_suggestions(query, final_response)

        yield {"event": "sources", "data": ",".join(sources)}
        yield {"event": "suggestions", "data": "|".join(suggestions)}
        yield {"event": "metadata", "data": json.dumps({"feedback_enabled": True})}
        yield {"event": "done", "data": ""}

        # Save the complete response to the temporary cache with source information
        await save_to_temp_cache(query, final_response, sources, source="gemini")

    except Exception as e:
        error_message = str(e)
        logging.error(f"Error in streaming response: {error_message}")
        if "429" in error_message:
            user_message = "We are currently experiencing high traffic. Please try again in a few moments."
            yield {"event": "error", "data": user_message}
        else:
            yield {"event": "error", "data": error_message}

@router.post(
    "/stream",
    summary="Stream a chat response",
    description="Stream a chat response in real-time using Server-Sent Events (SSE)",
    response_description="An EventSourceResponse that streams the response in real-time",
)
async def stream_chat(request: StreamingChatRequest):
    """
    Stream a chat response in real-time using Server-Sent Events (SSE).
    
    - **query**: The user's question or message
    - **session_id**: Optional unique identifier for the chat session
    """
    if not request.session_id:
        request.session_id = str(uuid.uuid4())
    
    return EventSourceResponse(
        stream_response(request.query, request.session_id),
        media_type="text/event-stream"
    )

@router.post(
    "/feedback",
    summary="Submit feedback for a chat response",
    description="Submit thumbs up or thumbs down feedback for a chat response, storing negative feedback in MongoDB",
    response_description="Status of the feedback submission",
)
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback for a chat response.
    
    - **session_id**: Unique identifier for the chat session
    - **query**: The user's query
    - **response**: The AI-generated response
    - **feedback**: 'positive' or 'negative'
    - **timestamp**: When the feedback was submitted
    - **additional_comments**: Optional user comments
    - **user_id**: Optional Firebase user ID
    - **user_email**: Optional user email
    - **user_name**: Optional user display name
    """
    try:
        feedback_data = {
            "session_id": feedback.session_id,
            "query": feedback.query,
            "response": feedback.response,
            "feedback": feedback.feedback,
            "timestamp": feedback.timestamp,
            "additional_comments": feedback.additional_comments,
            "user_id": feedback.user_id,
            "user_email": feedback.user_email,
            "user_name": feedback.user_name
        }
        success = await save_feedback(feedback_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save feedback")
        
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        logging.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/sessions/{session_id}",
    summary="Delete a chat session",
    description="Delete a chat session by its ID",
    response_description="A confirmation message",
)
async def delete_session(session_id: str):
    """
    Delete a chat session by its ID.
    
    - **session_id**: The ID of the session to delete
    """
    if session_id in active_sessions:
        del active_sessions[session_id]
        return {"message": f"Session {session_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

@router.get(
    "/sessions",
    summary="List all active chat sessions",
    description="Get a list of all active chat sessions",
    response_description="A list of session IDs and their metadata",
)
async def list_sessions():
    """List all active chat sessions with metadata."""
    return {
        "sessions": [
            {"id": session_id, "created_at": data["created_at"], 
             "last_active": data.get("last_active"), "query_count": len(data.get("queries", []))}
            for session_id, data in active_sessions.items()
        ]
    }

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming chat responses specifically for React Native apps.
    
    - **session_id**: Unique identifier for the chat session
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message from React Native app
            data = await websocket.receive_text()
            
            # Try to parse as JSON first
            try:
                json_data = json.loads(data)
                query = json_data.get("query")
            except json.JSONDecodeError:
                # If not JSON, treat the entire message as the query
                query = data
            
            if not query:
                await websocket.send_json({"event": "error", "data": "No query provided"})
                continue
                
            # Process the query using the existing streaming logic
            async for event in stream_response(query, session_id):
                # Send each event over WebSocket
                await websocket.send_json(event)
                
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        await websocket.close()
