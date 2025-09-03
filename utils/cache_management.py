import logging
from fastapi import APIRouter, Depends, HTTPException
from utils.cache_utils import query_cache
from utils.models import CacheStatsResponse, CacheClearResponse, PrecacheRequest, PrecacheResponse
from typing import Dict, Any, List

@router.delete("/clear", response_model=CacheClearResponse)
async def clear_all_cache():
    """Clear entire cache across all sessions"""
    try:
        total_entries = 0
        for session_data in query_cache.cache.values():
            total_entries += len(session_data["queries"])
        
        query_cache.cache.clear()
        
        return CacheClearResponse(
            message="Entire cache cleared successfully",
            entries_cleared=total_entries
        )
    except Exception as e:
        logging.error(f"Error clearing all cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/precache", response_model=PrecacheResponse)
async def precache_items(request: PrecacheRequest):
    """Pre-cache a list of question-answer pairs"""
    try:
        items_to_cache = [
            {
                "question": item.question,
                "answer": item.answer,
                "sources": item.sources,
                "session_id": item.session_id
            }
            for item in request.items
        ]
        
        items_cached = await query_cache.precache_items(items_to_cache)
        
        return PrecacheResponse(
            message=f"Successfully pre-cached {items_cached}/{len(request.items)} items",
            items_cached=items_cached
        )
    except Exception as e:
        logging.error(f"Error pre-caching items: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))