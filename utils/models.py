from pydantic import BaseModel, HttpUrl

class ChatRequest(BaseModel):
    query: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    sources: list[str] = []

class CrawlRequest(BaseModel):
    url: HttpUrl
    max_pages: int = 10
    depth: int = 2

class CrawlResponse(BaseModel):
    message: str
    documents_indexed: int
