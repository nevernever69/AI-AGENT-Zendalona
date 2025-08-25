from fastapi import APIRouter, HTTPException, Body, UploadFile, File, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import csv
import io
from utils.cache_utils import add_to_cache, get_from_cache, update_in_cache, delete_from_cache, get_cache_summary, get_cache_count
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

class CacheUpdateRequest(BaseModel):
    question: str
    answer: str

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

@router.put("/update/{entry_id}")
async def update_cache_entry(entry_id: str, request: CacheUpdateRequest):
    try:
        success = update_in_cache(entry_id, request.question, request.answer)
        if success:
            return {"success": True, "message": "Cache entry updated successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to update cache entry.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_cache_from_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        try:
            # Try decoding with UTF-8 first
            content_decoded = content.decode('utf-8')
        except UnicodeDecodeError:
            # If UTF-8 fails, try latin-1 as a fallback
            content_decoded = content.decode('latin-1')

        csv_reader = csv.reader(io.StringIO(content_decoded))
        header = next(csv_reader)  # Skip header
        logging.info("Starting CSV import...")

        for i, row in enumerate(csv_reader):
            if not row:  # Skip empty rows
                logging.warning(f"Skipping empty row at index {i}")
                continue
            try:
                # Assumes 'Sl, No.', 'QUESTION', 'ANSWER' format
                _, question, answer = row
                logging.info(f"Processing row {i+1}: Question: {question[:50]}...")
                success = add_to_cache(question, answer, source="csv_import")
                if not success:
                    logging.error(f"Failed to add row {i+1} to cache. Question: {question[:50]}...")
                else:
                    logging.info(f"Successfully added row {i+1} to cache.")

            except ValueError:
                # Log the problematic row and continue
                logging.warning(f"Skipping malformed row at index {i}: {row}")
                continue
        
        logging.info("CSV import finished.")
        return {"success": True, "message": "Cache imported successfully."}
    except Exception as e:
        logging.error(f"Failed to import CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to import CSV: {e}")

@router.delete("/delete/{entry_id}")
async def delete_cache_entry(entry_id: str):
    try:
        success = delete_from_cache(entry_id)
        if success:
            return {"success": True, "message": "Cache entry deleted successfully."}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete cache entry.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import Query
from utils.cache_utils import get_cache_summary, get_cache_count
from fastapi import APIRouter
from fastapi.responses import JSONResponse
@router.get("/export")
async def export_cache_to_csv():
    try:
        count, questions = get_cache_summary()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['question', 'answer', 'source'])
        for entry in questions:
            writer.writerow([entry['question'], entry['answer'], entry.get('source', 'manual')])
        output.seek(0)
        
        # Convert StringIO to BytesIO for proper CSV response
        output_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        output_bytes.seek(0)
        
        return StreamingResponse(
            output_bytes, 
            media_type="text/csv", 
            headers={"Content-Disposition": "attachment; filename=cache_export.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
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
