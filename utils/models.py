from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List, Dict, Any
import uuid

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's question or message", 
                      example="Tell me about Zendalona products")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()), 
                           description="Unique identifier for the chat session")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What features do Zendalona products have?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class StreamingChatRequest(BaseModel):
    query: str = Field(..., description="The user's question or message",
                      example="Tell me about Zendalona products")
    session_id: Optional[str] = Field(default=None, 
                           description="Optional unique identifier for the chat session")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What features do Zendalona products have?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI-generated response")
    sources: List[str] = Field(default_factory=list, 
                              description="List of sources used to generate the response")
    
    class Config:
        schema_extra = {
            "example": {
                "response": "Zendalona products offer accessibility features designed for users with diverse needs. Their key features include screen reader compatibility, customizable interfaces, and voice control options.",
                "sources": ["zendalona_website.pdf", "product_guide.pdf"]
            }
        }

class CrawlRequest(BaseModel):
    url: HttpUrl = Field(..., description="The URL to crawl", 
                        example="https://example.com")
    max_pages: int = Field(default=10, ge=1, le=100, 
                          description="Maximum number of pages to crawl")
    depth: int = Field(default=2, ge=1, le=5, 
                      description="Maximum crawl depth")
    
    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com",
                "max_pages": 15,
                "depth": 2
            }
        }

class CrawlResponse(BaseModel):
    message: str = Field(..., description="Status message about the crawl operation")
    documents_indexed: int = Field(..., description="Number of documents indexed")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Successfully crawled and indexed 12 documents from https://example.com",
                "documents_indexed": 12
            }
        }

class PdfUploadResponse(BaseModel):
    message: str = Field(..., description="Status message about the PDF processing")
    documents_indexed: int = Field(..., description="Number of pages indexed from the PDF")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Successfully processed and indexed 5 pages from PDF: product_manual.pdf",
                "documents_indexed": 5
            }
        }

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "An error occurred while processing your request"
            }
        }

class SessionInfo(BaseModel):
    id: str = Field(..., description="Session identifier")
    created_at: float = Field(..., description="Timestamp when the session was created")
    last_active: Optional[float] = Field(None, description="Timestamp of the last activity")
    query_count: int = Field(..., description="Number of queries in this session")

class SessionListResponse(BaseModel):
    sessions: List[SessionInfo] = Field(..., description="List of active sessions")
    
class SessionListResponse(BaseModel):
    sessions: List[SessionInfo] = Field(..., description="List of active sessions")
    
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