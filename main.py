from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import List, Dict, Any, AsyncGenerator, Optional
import logging
import asyncio
import uuid
import time
from io import BytesIO

# Import routers
from routers import chat, indexing, system
from utils.langchain_utils import get_rag_chain, process_query, get_streaming_chain
from utils.chroma_utils import process_pdf, index_documents_to_chroma
from crawler.crawler import process_and_index_url
from config import settings

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)

# Create FastAPI app
app = FastAPI(
    title="Zendalona Chatbot API",
    description="""
    REST API for an accessible chatbot using LangChain, Gemini, and ChromaDB.
    This API provides endpoints for chatting with the bot, streaming responses,
    indexing content from websites, and uploading PDFs for knowledge base enrichment.
    """,
    version="0.2.0",
    docs_url=None,
    redoc_url=None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(indexing.router)
app.include_router(system.router)

# Custom OpenAPI endpoint
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Swagger UI",
        swagger_favicon_url="",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)