import logging
from fastapi import FastAPI, HTTPException
from utils.models import ChatRequest, ChatResponse, CrawlRequest, CrawlResponse
from utils.langchain_utils import get_rag_chain, process_query
from crawler.crawler import process_and_index_url
from config import settings

# Setup logging
logging.basicConfig(filename=settings.log_path, level=logging.INFO)

app = FastAPI(
    title="Zendalona Chatbot API",
    description="Backend for an accessible chatbot using LangChain, Gemini, and ChromaDB",
    version="0.1.0"
)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        chain = get_rag_chain()
        response, sources = process_query(chain, request.query)
        logging.info(f"Processed query: {request.query}")
        return ChatResponse(response=response, sources=sources)
    except Exception as e:
        logging.error(f"Error processing chat query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/crawl", response_model=CrawlResponse)
async def crawl(request: CrawlRequest):
    try:
        documents_indexed = await process_and_index_url(  # Changed to await
            str(request.url), request.max_pages, request.depth
        )
        message = f"Successfully crawled and indexed {documents_indexed} documents from {request.url}"
        logging.info(message)
        return CrawlResponse(message=message, documents_indexed=documents_indexed)
    except Exception as e:
        logging.error(f"Error crawling {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
