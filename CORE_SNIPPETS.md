# Core Code Snippets and Architecture

## 1. Main Application Setup

### FastAPI Application (main.py)
```python
app = FastAPI(
    title="Zendalona Chatbot API",
    description="""
    REST API for an accessible chatbot using LangChain, Gemini, and ChromaDB.
    This API provides endpoints for chatting with the bot, streaming responses,
    indexing content from websites, and uploading PDFs for knowledge base enrichment.
    
    ## WebSocket Support
    For React Native applications, a WebSocket endpoint is available at `/chat/ws/{session_id}` 
    for streaming responses. This endpoint provides the same functionality as the SSE `/chat/stream` 
    endpoint but uses WebSocket protocol which works better with React Native.
    """,
    version="0.3.0",
    docs_url=None,
    redoc_url=None,
)

# Include routers
app.include_router(chat.router)
app.include_router(indexing.router)
app.include_router(system.router)
app.include_router(cache.router)
app.include_router(temp_cache.router)
app.include_router(feedback.router)
app.include_router(debug.router)
```

## 2. Chat Processing Core

### Chat Endpoint (routers/chat.py)
```python
@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # 1. Check cache first
    cached_results = get_from_cache(request.query)
    
    if cached_results and similarity >= threshold:
        # Return cached response
        return ChatResponse(response=answer, sources=sources, suggestions=[], feedback_enabled=True)
    
    # 2. If no cache match, call Gemini API
    chain = get_rag_chain()
    response, sources = process_query(chain, request.query)
    
    # 3. Cache the new response
    await save_to_temp_cache(request.query, response, sources, source="gemini")
    
    return ChatResponse(response=response, sources=sources, suggestions=[], feedback_enabled=True)
```

### Streaming Response (routers/chat.py)
```python
async def stream_response(query: str, session_id: str) -> AsyncGenerator[dict, None]:
    # 1. Check cache first
    cached_results = get_from_cache(query)
    
    if cached_results and similarity >= threshold:
        # Stream cached response word by word
        words = answer.split()
        for word in words:
            yield {"event": "message", "data": f"{word} "}
            await asyncio.sleep(0.05)
        return
    
    # 2. If no cache match, retrieve context and call LLM
    chain = get_streaming_chain()
    docs = retriever.get_relevant_documents(query)
    context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
    
    # 3. Stream LLM response
    async for chunk in chain.astream({"context": context, "question": query}):
        content = chunk.content if hasattr(chunk, "content") else str(chunk)
        yield {"event": "message", "data": content}
        await asyncio.sleep(0.01)
```

## 3. LangChain Integration

### RAG Chain Setup (utils/langchain_utils.py)
```python
def get_rag_chain():
    db = get_chroma_db()
    retriever = db.as_retriever(search_kwargs={"k": settings.retrieval_k})
    
    template = """
You are a helpful assistant for Zendalona, a company providing accessibility solutions.
Answer the question based only on the following context:
{context}

Question: {question}

Instructions:
- If the question is a simple greeting (like "hi", "hello", "hey") with no other content, respond ONLY with: "Hello! How can I help you with Zendalona today?"
- If the question is asking for specific information, answer ONLY that information directly without any greeting
- Keep responses focused and under 5 sentences unless specifically asked for details
"""

    prompt = PromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )
    
    return chain
```

### LLM Configuration (utils/langchain_utils.py)
```python
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite", 
        temperature=0.3,  # Lower temperature for more consistent responses
        google_api_key=settings.gemini_api_key
    )
```

## 4. Vector Database Operations

### ChromaDB Setup (utils/chroma_utils.py)
```python
def get_chroma_db(collection_name: str = "zendalona"):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.gemini_api_key
    )
    return Chroma(
        collection_name=collection_name,
        persist_directory=settings.chroma_db_path,
        embedding_function=embeddings
    )
```

### Document Indexing (utils/chroma_utils.py)
```python
def index_documents_to_chroma(documents: list[Document], collection_name: str = "zendalona") -> int:
    db = get_chroma_db(collection_name)
    
    # Get existing document URLs/sources to avoid duplicates
    existing_docs = db.get(include=["metadatas"])
    existing_sources = {doc["source"] for doc in existing_docs["metadatas"] if "source" in doc}
    
    # Filter out documents whose sources are already indexed
    new_documents = [doc for doc in documents if doc.metadata.get("source") not in existing_sources]
    
    # Add new documents to ChromaDB
    db.add_documents(new_documents)
    return len(new_documents)
```

## 5. Caching System

### Cache Retrieval (utils/cache_utils.py)
```python
def get_from_cache(question: str, k: int = 5) -> List[Tuple[Document, float]]:
    try:
        # First, try exact match for common greetings
        common_greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
        normalized_question = question.lower().strip()
        
        if normalized_question in common_greetings:
            db = get_chroma_db(collection_name=CACHE_COLLECTION_NAME)
            # Get all documents and check for exact match
            all_docs = db.get(include=["documents", "metadatas"])
            for i, doc_content in enumerate(all_docs["documents"]):
                if doc_content.lower().strip() == normalized_question:
                    # Return with a very high similarity score (low distance)
                    return [(doc, 0.01)]
        
        # If no exact match for greetings, use similarity search
        db = get_chroma_db(collection_name=CACHE_COLLECTION_NAME)
        results = db.similarity_search_with_score(question, k=k)
        return results
    except Exception as e:
        logger.error(f"Error querying cache: {str(e)}")
        return []
```

### Cache Filtering (utils/cache_utils.py)
```python
def get_from_cache(question: str, k: int = 5) -> List[Tuple[Document, float]]:
    db = get_chroma_db(collection_name=CACHE_COLLECTION_NAME)
    results = db.similarity_search_with_score(question, k=k)
    
    # Filter by similarity threshold
    filtered_results = []
    for doc, score in results:
        similarity = 1.0 - score
        threshold = 0.65 if len(question) > 10 else 0.50
        if similarity >= threshold:
            filtered_results.append((doc, score))
    
    return filtered_results
```

## 6. Configuration Management

### Settings (config.py)
```python
class Settings(BaseSettings):
    # Vector DB settings
    chroma_db_path: str
    retrieval_k: int = 6          # Initial documents to retrieve
    retrieval_threshold: float = 0.7  # Similarity threshold
    max_context_docs: int = 4     # Max documents to pass to LLM
    
    # API Keys
    gemini_api_key: str
    mongodb_uri: str
    
    # Crawler settings
    crawler_depth: int
    crawler_max_pages: int
    
    # Feature flags
    disable_gemini_call: bool = False
```

## 7. Data Models

### Chat Request/Response (utils/models.py)
```python
class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's question or message")
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class ChatResponse(BaseModel):
    response: str = Field(..., description="The AI-generated response")
    sources: List[str] = Field(default_factory=list, description="List of sources used")
    suggestions: List[str] = Field(default_factory=list, description="Suggested questions")
    feedback_enabled: bool = Field(True, description="Whether feedback can be submitted")
```

## 8. Key Design Patterns

### 1. Separation of Concerns
- **Routers**: Handle HTTP requests and responses
- **Utils**: Business logic and external service integration
- **Models**: Data structures and validation

### 2. Caching Strategy
- **Two-level cache**: ChromaDB (permanent) + MongoDB (temporary)
- **Similarity-based**: Uses vector similarity for cache matching
- **Threshold filtering**: Configurable similarity thresholds

### 3. Streaming Architecture
- **SSE Support**: Server-Sent Events for web clients
- **WebSocket Support**: For React Native applications
- **Chunked Responses**: Word-by-word streaming for better UX

### 4. Error Handling
- **Comprehensive logging**: Detailed logging for debugging
- **Graceful degradation**: Fallback responses when services fail
- **User-friendly errors**: Clear error messages for clients

## 9. Performance Optimizations

### Context Filtering
```python
# Retrieve more documents initially and filter by similarity threshold
all_docs_with_scores = get_chroma_db().similarity_search_with_score(query, k=settings.retrieval_k)
# Filter by similarity threshold
filtered_docs = [doc for doc, score in all_docs_with_scores if score <= settings.retrieval_threshold]
# Limit to maximum number of context documents
docs = filtered_docs[:settings.max_context_docs] if filtered_docs else []
```

### Efficient Chain Construction
```python
# Use RunnablePassthrough for efficient chain construction
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | get_llm()
    | StrOutputParser()
)
```

This architecture provides a scalable, maintainable, and efficient chatbot backend that can be easily extended and customized.
```