from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from utils.cache_utils import add_to_cache, get_from_cache
from utils.models import ChatResponse

router = APIRouter(prefix="/cache", tags=["Cache"])

class CacheEntryRequest(BaseModel):
    question: str = Field(..., description="The question to cache", 
                       example="What is Zendalona's flagship product?")
    answer: str = Field(..., description="The answer to cache",
                      example="Zendalona's flagship product is Accessible-Coconut, which provides screen reading capabilities.")
    source: str = Field(default="manual", description="Source of the cached answer",
                      example="manual")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What is Zendalona's flagship product?",
                "answer": "Zendalona's flagship product is Accessible-Coconut, which provides screen reading capabilities.",
                "source": "manual"
            }
        }

class CacheAddResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")

@router.post(
    "/add",
    response_model=CacheAddResponse,
    summary="Add an entry to the response cache",
    description="Add a question-answer pair to the cache for future use",
    response_description="Status of the cache operation",
)
async def add_cache_entry(request: CacheEntryRequest):
    """
    Add a question-answer pair to the cache.
    
    - **question**: The question to cache
    - **answer**: The answer to cache
    - **source**: Optional source of the answer (default: "manual")
    """
    try:
        success = add_to_cache(request.question, request.answer, request.source)
        
        if success:
            return CacheAddResponse(
                success=True,
                message=f"Successfully added question to cache: '{request.question[:50]}...'"
            )
        else:
            return CacheAddResponse(
                success=False,
                message="Failed to add question to cache"
            )
    except Exception as e:
        logging.error(f"Error adding cache entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import Query
from utils.cache_utils import get_cache_summary
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.cache_utils import get_cache_count
# from utils.cache_utils import clear_cache

# @router.delete("clear")
# async def clear_cache_endpoint():
#     success = clear_cache()
#     if success:
#         return JSONResponse(content={"success": True, "message": "Cache cleared successfully."})
#     else:
#         return JSONResponse(content={"success": False, "message": "Failed to clear cache."}, status_code=500)


@router.get("/count")
async def cache_count():
    try:
        count = get_cache_count()
        return JSONResponse(content={"success": True, "count": count})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

@router.get("/summary")
async def cache_summary(limit: Optional[int] = Query(None, description="Maximum number of questions to return")):
    try:
        count, questions = get_cache_summary(limit=limit)
        return JSONResponse(content={
            "success": True,
            "count": count,
            "questions": questions
        })
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


@router.get(
    "/check/{question}",
    response_model=ChatResponse,
    summary="Check if a question exists in the cache",
    description="Check if a similar question exists in the cache and return the answer if found",
    response_description="The cached answer if found, otherwise an error",
)
async def check_cache(question: str):
    """
    Check if a question exists in the cache.
    
    - **question**: The question to look up in the cache
    """
    try:
        found, answer, sources = get_from_cache(question)
        
        if found:
            return ChatResponse(response=answer, sources=sources)
        else:
            raise HTTPException(status_code=404, detail="No cached answer found")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error checking cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
