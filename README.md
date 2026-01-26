# Zendalona AI Chatbot Backend
<p align="center">
  <b>An intelligent RAG-powered chatbot backend for accessibility solutions</b>
</p>

---

## About The Project

This project was developed as part of **Google Summer of Code 2025** for [Zendalona](https://zendalona.com). It provides a production-ready REST API backend for an AI-powered chatbot that specializes in answering questions about accessibility products and solutions.

The system uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware responses by combining a vector database of curated knowledge with Google's Gemini LLM.

### Key Highlights

- **Intelligent Responses**: Uses RAG with LangChain and Google Gemini for accurate, contextual answers
- **Dual-Layer Caching**: Optimized response times with ChromaDB permanent cache and MongoDB temporary cache
- **Real-time Streaming**: Server-Sent Events (SSE) and WebSocket support for streaming responses
- **Dynamic Knowledge Base**: Enrich the knowledge base through web crawling and PDF uploads
- **Admin Dashboard Ready**: Comprehensive feedback management and cache curation system

---

## Features

### Chat System
- Complete chat responses with source citations
- Real-time response streaming via SSE
- WebSocket support for React Native and mobile apps
- Session management and tracking
- Smart similarity-based caching with dynamic thresholds

### Document Indexing
- Async web crawling with configurable depth (1-5 levels)
- PDF document upload and extraction
- Automatic duplicate detection
- Collection management (create, list, delete)

### Caching Architecture
| Layer | Storage | Purpose |
|-------|---------|---------|
| **Permanent** | ChromaDB | Curated Q&A pairs for fast retrieval |
| **Temporary** | MongoDB | Auto-expiring (8-day TTL) responses for admin review |

### Admin Features
- User feedback collection and management
- Promote responses from temp cache to permanent cache
- CSV import/export for cache management
- System health monitoring and debugging tools

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Request                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  Chat   │ │Indexing │ │  Cache  │ │Feedback │ │ System  │  │
│  │ Router  │ │ Router  │ │ Router  │ │ Router  │ │ Router  │  │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
└───────┼──────────┼──────────┼──────────┼──────────┼──────────┘
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Utility Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  LangChain   │  │   ChromaDB   │  │   MongoDB    │          │
│  │    Utils     │  │    Utils     │  │    Utils     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Google Gemini  │ │    ChromaDB     │ │     MongoDB     │
│      API        │ │  Vector Store   │ │    Database     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Query Processing Flow

```
User Query
    │
    ├─► Cache Check (ChromaDB similarity search)
    │       │
    │       ├─► Match Found → Return cached answer
    │       │
    │       └─► No Match
    │               │
    │               ▼
    │           Retrieve Documents (top-k similar)
    │               │
    │               ▼
    │           Generate Response (Gemini LLM)
    │               │
    │               ▼
    │           Save to Temp Cache
    │
    └─► Return Response to Client
```

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.115+ |
| **LLM** | Google Gemini (via google-genai) |
| **RAG Framework** | LangChain 0.3+ |
| **Vector Database** | ChromaDB |
| **Document Database** | MongoDB (Motor async driver) |
| **Web Crawling** | Crawl4AI |
| **PDF Processing** | PyPDF2 |
| **Server** | Uvicorn |

---

## Getting Started

### Prerequisites

- Python 3.13 or higher
- MongoDB instance (local or cloud)
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/zendalona/AI-AGENT-Zendalona.git
   cd AI-AGENT-Zendalona
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   gemini_api_key=your_gemini_api_key_here
   mongodb_uri=mongodb://localhost:27017/
   mongodb_database=zendalona
   PORT=10000
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the API documentation**
   - Swagger UI: http://localhost:10000/docs
   - ReDoc: http://localhost:10000/redoc

### Docker Deployment

```bash
# Build the image
docker build -t zendalona-chatbot .

# Run the container
docker run -d \
  -p 10000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e MONGODB_URI=mongodb://host:27017/ \
  --name zendalona-bot \
  zendalona-chatbot
```

---

## API Reference

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Get a complete chat response |
| `POST` | `/chat/stream` | Stream response via SSE |
| `WS` | `/chat/ws/{session_id}` | WebSocket streaming |
| `POST` | `/chat/feedback` | Submit user feedback |

### Indexing Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/indexing/crawl` | Crawl a website |
| `POST` | `/indexing/upload-pdf` | Upload and index a PDF |
| `GET` | `/indexing/collections` | List all collections |
| `DELETE` | `/indexing/collections/{name}` | Delete a collection |

### Cache Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/cache/add` | Add a cache entry |
| `PUT` | `/cache/update/{id}` | Update a cache entry |
| `DELETE` | `/cache/{id}` | Delete a cache entry |
| `GET` | `/cache/export` | Export cache as CSV |
| `POST` | `/cache/import` | Import cache from CSV |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/system/health` | Health check |
| `GET` | `/system/info` | System information |

For complete API documentation, run the server and visit `/docs`.

---

## Project Structure

```
AI-AGENT-Zendalona/
├── main.py                 # Application entry point
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container configuration
├── .env.example            # Environment template
│
├── routers/                # API endpoint definitions
│   ├── chat.py             # Chat endpoints
│   ├── indexing.py         # Document indexing
│   ├── cache.py            # Cache management
│   ├── temp_cache.py       # Temporary cache
│   ├── feedback.py         # User feedback
│   ├── system.py           # System monitoring
│   └── auth.py             # Authentication
│
├── utils/                  # Core utilities
│   ├── langchain_utils.py  # RAG chain setup
│   ├── chroma_utils.py     # Vector DB operations
│   ├── cache_utils.py      # Cache operations
│   ├── mongo_utils.py      # MongoDB operations
│   └── models.py           # Pydantic schemas
│
├── crawler/                # Web crawling module
│   └── crawler.py          # AsyncWebCrawler
│
└── chroma_db/              # Vector database storage
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `gemini_api_key` | Google Gemini API key | Required |
| `mongodb_uri` | MongoDB connection string | `mongodb://localhost:27017/` |
| `mongodb_database` | Database name | `zendalona` |
| `chroma_db_path` | ChromaDB storage path | `./chroma_db` |
| `PORT` | Server port | `10000` |
| `crawler_depth` | Web crawling depth (1-5) | `2` |
| `crawler_max_pages` | Max pages to crawl | `50` |
| `retrieval_k` | Documents to retrieve | `6` |
| `retrieval_threshold` | Similarity threshold | `0.7` |

---


## Contributing

Contributions are welcome! This project continues to be developed and improved.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---


