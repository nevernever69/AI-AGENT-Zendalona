from fastapi import APIRouter, HTTPException, UploadFile, File, Path, Query
from typing import List, Optional
from utils.models import CrawlRequest, CrawlResponse, PdfUploadResponse
from utils.chroma_utils import process_pdf, index_documents_to_chroma
from crawler.crawler import process_and_index_url
import logging
from io import BytesIO
router = APIRouter(prefix="/indexing", tags=["Indexing"])

@router.post(
    "/crawl",
    response_model=CrawlResponse,
    summary="Crawl and index a website",
    description="Crawl a website and index its content into the vector database",
    response_description="Details about the indexed documents",
)
async def crawl(request: CrawlRequest):
    """
    Crawl a website and index its content into the vector database.
    
    - **url**: The URL to crawl
    - **max_pages**: Maximum number of pages to crawl (default: 10)
    - **depth**: Maximum crawl depth (default: 2)
    """
    try:
        documents_indexed = await process_and_index_url(
            str(request.url), request.max_pages, request.depth
        )
        message = f"Successfully crawled and indexed {documents_indexed} documents from {request.url}"
        logging.info(message)
        return CrawlResponse(message=message, documents_indexed=documents_indexed)
    except Exception as e:
        logging.error(f"Error crawling {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/upload-pdf",
    response_model=PdfUploadResponse,
    summary="Upload and index a PDF",
    description="Upload and process a PDF file, indexing its content into the vector database",
    response_description="Details about the indexed PDF pages",
)
async def upload_pdf(
    file: UploadFile = File(..., description="The PDF file to upload and process"),
    collection_name: str = Query("zendalona", description="The collection name to store the indexed content")
):
    """
    Upload and process a PDF file, indexing its content into the vector database.
    
    - **file**: The PDF file to upload and process
    - **collection_name**: Optional collection name for indexing (default: "zendalona")
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file content
        content = await file.read()
        documents = process_pdf(BytesIO(content), file.filename)
        
        # Index documents in ChromaDB
        documents_indexed = index_documents_to_chroma(documents, collection_name=collection_name)
        
        message = f"Successfully processed and indexed {documents_indexed} pages from PDF: {file.filename}"
        logging.info(message)
        return PdfUploadResponse(message=message, documents_indexed=documents_indexed)
    except Exception as e:
        logging.error(f"Error processing PDF upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/collections",
    summary="List all collections",
    description="List all collections in the vector database",
    response_description="A list of collection names",
)
async def list_collections():
    """List all available collections in the vector database."""
    try:
        # This is a placeholder - you'll need to implement logic to get collections from ChromaDB
        # For now, return a simple response
        return {"collections": ["zendalona"]}
    except Exception as e:
        logging.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))