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
from routers import chat, indexing, system, cache, temp_cache, feedback, debug
from utils.langchain_utils import get_rag_chain, process_query, get_streaming_chain
from utils.chroma_utils import process_pdf, index_documents_to_chroma
from crawler.crawler import process_and_index_url
from config import settings

# Setup logging
from logging.config import dictConfig
import logging

# Define the logging configuration
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": settings.log_path,
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {"handlers": ["default", "file"], "level": "INFO"},
    },
}

# Apply the logging configuration
dictConfig(log_config)

# Create FastAPI app
app = FastAPI(
    title="Zendalona Chatbot API",
    description="""
    REST API for an accessible chatbot using LangChain, Gemini, and ChromaDB.
    This API provides endpoints for chatting with the bot, streaming responses,
    indexing content from websites, and uploading PDFs for knowledge base enrichment.
    """,
    version="0.3.0",
    docs_url=None,
    redoc_url=None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(indexing.router)
app.include_router(system.router)
app.include_router(cache.router)
app.include_router(temp_cache.router)
app.include_router(feedback.router)
app.include_router(debug.router)

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
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)