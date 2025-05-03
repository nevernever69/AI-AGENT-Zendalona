from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any, AsyncGenerator, Optional, List
from utils.models import ChatRequest, ChatResponse, StreamingChatRequest
from utils.langchain_utils import get_rag_chain, process_query, get_streaming_chain
from utils.cache_utils import get_from_cache, cache_chatbot_response
import logging
import asyncio
import uuid
import time

router = APIRouter(prefix="/chat", tags=["Chat"])

# Track active chat sessions
active_sessions: Dict[str, Dict[str, Any]] = {}

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
        # First, try to find a similar question in the cache
        found, cached_answer, cached_sources = get_from_cache(request.query)
        
        if found:
            logging.info(f"Returning cached response for query: {request.query}")
            return ChatResponse(response=cached_answer, sources=cached_sources)
        
        # If no cache hit, proceed with Gemini API
        chain = get_rag_chain()
        response, sources = process_query(chain, request.query)
        logging.info(f"Processed query with Gemini: {request.query}")
        
        # Cache the response for future use
        cache_chatbot_response(request.query, response, sources)
        
        return ChatResponse(response=response, sources=sources)
    except Exception as e:
        logging.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def stream_response(query: str, session_id: str) -> AsyncGenerator[dict, None]:
    """Generate a streaming response for the chat query."""
    try:
        # Check cache first for streaming responses too
        found, cached_answer, cached_sources = get_from_cache(query)
        
        if found:
            logging.info(f"Streaming cached response for query: {query}")
            # Send the cached response in chunks to simulate streaming
            words = cached_answer.split()
            chunk_size = max(1, len(words) // 10)  # Break into ~10 chunks
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                yield {"event": "message", "data": chunk}
                await asyncio.sleep(0.1)  # Simulate natural typing speed
            
            # Send sources as the final event
            yield {"event": "sources", "data": ",".join(cached_sources)}
            
            # Send completion event
            yield {"event": "done", "data": ""}
            return
        
        # Track the session
        if session_id not in active_sessions:
            active_sessions[session_id] = {"created_at": time.time(), "queries": []}
        active_sessions[session_id]["queries"].append(query)
        active_sessions[session_id]["last_active"] = time.time()
        
        # If no cache hit, initialize the RAG chain with streaming capability
        chain, retriever = get_streaming_chain()
        
        # Retrieve documents based on the query
        docs = retriever.get_relevant_documents(query)
        sources = [doc.metadata.get("source", "") for doc in docs if doc.metadata.get("source")]
        
        # Stream the response
        context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
        
        # Variables to collect the full response for caching
        full_response = []
        
        async for chunk in chain.astream({"context": context, "question": query}):
            if hasattr(chunk, "content"):
                full_response.append(chunk.content)
                yield {"event": "message", "data": chunk.content}
            else:
                full_response.append(str(chunk))
                yield {"event": "message", "data": str(chunk)}
            await asyncio.sleep(0.01)  # Small delay to control flow
        
        # Send sources as the final event
        yield {"event": "sources", "data": ",".join(sources)}
        
        # Send completion event
        yield {"event": "done", "data": ""}
        
        # Cache the complete response
        cache_chatbot_response(query, "".join(full_response), sources)
        
    except Exception as e:
        logging.error(f"Error in streaming response: {str(e)}")
        yield {"event": "error", "data": str(e)}
        
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