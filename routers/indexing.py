from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from typing import List
from utils.chroma_utils import process_pdf, index_documents_to_chroma, list_collections, delete_collection, get_collection_documents, delete_document_from_collection, process_and_index_file
from crawler.crawler import process_and_index_url
from utils.cache_utils import get_cache_summary, delete_from_cache
from io import BytesIO
from pydantic import BaseModel

class CrawlRequest(BaseModel):
    url: str
    max_pages: int = 10
    depth: int = 2

router = APIRouter(prefix="/indexing", tags=["Indexing"])

@router.post("/crawl", summary="Crawl and index a website")
async def crawl(request: CrawlRequest, force_reindex: bool = Query(False, description="Force reindex even if content already exists")):
    try:
        pages_indexed = await process_and_index_url(request.url, request.max_pages, request.depth)
        return {"message": f"Successfully indexed {pages_indexed} pages from {request.url}", "pages_indexed": pages_indexed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import", summary="Import and process a file")
async def import_file(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        documents = process_and_index_file(file_content, file.filename)
        if not documents:
            return {"message": "No content found in file or failed to process.", "pages_indexed": 0}
        
        pages_indexed = index_documents_to_chroma(documents)
        return {"message": f"Successfully indexed {pages_indexed} pages from {file.filename}", "pages_indexed": pages_indexed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-pdf", summary="Upload and process a PDF")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    try:
        file_content = await file.read()
        documents = process_pdf(BytesIO(file_content), file.filename)
        if not documents:
            return {"message": "No content found in PDF or failed to process.", "pages_indexed": 0}
        
        pages_indexed = index_documents_to_chroma(documents)
        return {"message": f"Successfully indexed {pages_indexed} pages from {file.filename}", "pages_indexed": pages_indexed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collections", summary="List all collections")
def get_all_collections():
    collections = list_collections()
    return {"collections": collections}

@router.delete("/collections/{collection_name}", summary="Delete a collection")
def delete_single_collection(collection_name: str):
    if delete_collection(collection_name):
        return {"message": f"Collection '{collection_name}' deleted successfully."}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to delete collection '{collection_name}'.")

@router.get("/cache", summary="Get all cache entries")
def get_cache_entries():
    total, entries = get_cache_summary()
    return {"total": total, "entries": entries}

@router.delete("/cache/{entry_id}", summary="Delete a cache entry")
def delete_cache_entry(entry_id: str):
    if delete_from_cache(entry_id):
        return {"message": f"Cache entry with ID '{entry_id}' deleted successfully."}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to delete cache entry with ID '{entry_id}'.")

@router.get("/collections/{collection_name}", summary="Get all documents from a collection")
def get_documents_in_collection(collection_name: str):
    documents = get_collection_documents(collection_name)
    if documents is not None:
        return {"documents": documents}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to get documents from collection '{collection_name}'.")

@router.delete("/collections/{collection_name}/{document_id}", summary="Delete a document from a collection")
def delete_document(collection_name: str, document_id: str):
    if delete_document_from_collection(collection_name, document_id):
        return {"message": f"Document '{document_id}' deleted successfully from collection '{collection_name}'."}
    else:
        raise HTTPException(status_code=500, detail=f"Failed to delete document '{document_id}' from collection '{collection_name}'.")