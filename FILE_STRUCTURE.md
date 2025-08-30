# Backend File Structure

## Project Root
```
zendalona-chatbot/
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore patterns
├── ADMIN_DOCUMENTATION.md       # Administrative documentation
├── ARCHITECTURE.md              # System architecture documentation
├── CORE_SNIPPETS.md             # Core code snippets and explanations
├── Dockerfile                   # Docker configuration
├── FILE_STRUCTURE.md            # This file
├── main.py                      # FastAPI application entry point
├── pyproject.toml               # Project metadata and dependencies
├── requirements.txt             # Python dependencies
├── app.log                      # Application log file
├── checking.py                  # Utility script
├── clear_cache.py               # Cache clearing utility
├── clear_temp_cache.py          # Temporary cache clearing utility
├── config.py                    # Application configuration
├── debug_csv_import.py          # Debug utility
├── debug_fastapi_csv_import.py  # Debug utility
├── chroma_db/                   # ChromaDB vector database
│   ├── chroma.sqlite3           # Database file
│   └── */                       # Collection directories
├── crawler/                     # Web crawling module
│   ├── __init__.py
│   └── crawler.py               # Web crawling implementation
├── logs/                        # Log files directory
├── routers/                     # FastAPI routers
│   ├── __init__.py
│   ├── auth.py                  # Authentication endpoints
│   ├── cache.py                 # Cache management endpoints
│   ├── chat.py                  # Chat functionality endpoints
│   ├── debug.py                 # Debug endpoints
│   ├── feedback.py              # Feedback collection endpoints
│   ├── indexing.py              # Document indexing endpoints
│   ├── system.py                # System information endpoints
│   └── temp_cache.py            # Temporary cache endpoints
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── auth_utils.py            # Authentication utilities
│   ├── cache_management.py      # Cache management utilities
│   ├── cache_utils.py           # Cache utilities
│   ├── chroma_utils.py          # ChromaDB utilities
│   ├── langchain_utils.py       # LangChain integration utilities
│   ├── models.py                # Data models
│   ├── mongo_utils.py           # MongoDB utilities
│   └── response_utils.py        # Response processing utilities
└── Zendalona-UI/                # Frontend application
    ├── public/
    ├── src/
    └── package.json
```

## Detailed Component Descriptions

### Main Application (`main.py`)
- FastAPI application setup and configuration
- Router registration
- CORS middleware configuration
- Logging setup
- Custom OpenAPI and Swagger UI endpoints

### Configuration (`config.py`)
- Pydantic Settings class for environment configuration
- Database paths and connection settings
- API keys and service credentials
- Feature flags and toggles
- Crawler and indexing parameters

### Routers Directory
Each router handles a specific domain of functionality:

#### Chat Router (`routers/chat.py`)
- POST `/chat` - Standard chat endpoint
- POST `/chat/stream` - Streaming chat endpoint
- POST `/chat/feedback` - Feedback collection
- DELETE `/chat/sessions/{session_id}` - Session management
- GET `/chat/sessions` - Active sessions listing
- WebSocket `/chat/ws/{session_id}` - WebSocket streaming

#### Indexing Router (`routers/indexing.py`)
- POST `/index/url` - Web crawling and indexing
- POST `/index/pdf` - PDF document indexing
- GET `/index/documents` - Document listing
- DELETE `/index/documents/{document_id}` - Document removal

#### Cache Router (`routers/cache.py`)
- GET `/cache` - Cache summary
- POST `/cache` - Add to cache
- PUT `/cache/{entry_id}` - Update cache entry
- DELETE `/cache/{entry_id}` - Remove from cache
- GET `/cache/count` - Cache entry count

#### Temporary Cache Router (`routers/temp_cache.py`)
- GET `/temp-cache` - Temporary cache items
- DELETE `/temp-cache/clear` - Clear temporary cache
- PUT `/temp-cache/{item_id}` - Update temporary cache item
- POST `/temp-cache/move/{item_id}` - Move to permanent cache
- DELETE `/temp-cache/{item_id}` - Delete temporary cache item

#### Feedback Router (`routers/feedback.py`)
- GET `/feedback` - Retrieve feedback
- DELETE `/feedback/{feedback_id}` - Delete feedback
- GET `/feedback/stats` - Feedback statistics

#### System Router (`routers/system.py`)
- GET `/system/info` - System information
- GET `/system/logs` - Application logs
- GET `/system/status` - System status
- GET `/system/memory` - Memory usage

#### Authentication Router (`routers/auth.py`)
- POST `/auth/login` - User login
- POST `/auth/logout` - User logout
- GET `/auth/profile` - User profile
- POST `/auth/refresh` - Token refresh

#### Debug Router (`routers/debug.py`)
- GET `/debug/cache` - Debug cache contents
- GET `/debug/vector-db` - Debug vector database
- POST `/debug/test-query` - Test query endpoint

### Utilities Directory

#### LangChain Utilities (`utils/langchain_utils.py`)
- LLM configuration and initialization
- RAG chain construction
- Prompt template management
- Response processing functions

#### Chroma Utilities (`utils/chroma_utils.py`)
- Vector database connection management
- Document indexing and retrieval
- PDF processing functions
- Collection management operations

#### Cache Utilities (`utils/cache_utils.py`)
- Cache database operations
- Similarity search functions
- Cache entry management
- Filtering and threshold logic

#### MongoDB Utilities (`utils/mongo_utils.py`)
- Database connection management
- Feedback storage operations
- Temporary cache management
- CRUD operations for various collections

#### Authentication Utilities (`utils/auth_utils.py`)
- JWT token generation and validation
- Password hashing utilities
- User authentication functions
- Session management

#### Response Utilities (`utils/response_utils.py`)
- Response post-processing functions
- Repetitive phrase removal
- Text formatting utilities
- Response sanitization

#### Cache Management Utilities (`utils/cache_management.py`)
- Cache optimization functions
- Cache clearing operations
- Cache statistics collection
- Maintenance utilities

#### Models (`utils/models.py`)
- Pydantic data models for request/response validation
- Type definitions and examples
- Schema documentation

### Crawler Module (`crawler/crawler.py`)
- Web crawling functionality
- Content extraction and processing
- URL filtering and depth control
- Document creation for indexing

### Database Directories

#### ChromaDB (`chroma_db/`)
- Vector database storage
- Collection persistence
- Embedding storage

#### Logs (`logs/`)
- Application log files
- Error logs
- Debug information

### Frontend (`Zendalona-UI/`)
- React-based user interface
- Component structure
- State management
- API integration

## Key Dependencies

### Core Framework
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### AI and NLP
- `langchain` - LLM framework
- `langchain-chroma` - ChromaDB integration
- `langchain-google-genai` - Google Generative AI integration
- `google-generativeai` - Google AI SDK

### Vector Database
- `chromadb` - Vector database

### Web Scraping
- `crawl4ai` - Web crawling library
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML processing

### Database
- `motor` - Async MongoDB driver

### Utilities
- `python-dotenv` - Environment variables
- `python-multipart` - File upload support
- `sse-starlette` - Server-Sent Events
- `psutil` - System utilities

This structure provides a modular, maintainable architecture that separates concerns and allows for easy extension and testing.