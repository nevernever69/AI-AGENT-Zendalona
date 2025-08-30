# Frameworks and Dependencies Documentation for KT

## Overview
This document outlines the key frameworks, libraries, and dependencies used in the Zendalona Chatbot backend project. This information is essential for knowledge transfer (KT) sessions to help new team members understand the technology stack.

## Core Framework

### FastAPI
- **Version**: 0.115.2
- **Purpose**: The primary web framework for building the REST API
- **Key Features Used**:
  - Asynchronous request handling
  - Automatic OpenAPI/Swagger documentation
  - Built-in validation using Pydantic
  - Dependency injection system
  - CORS middleware for cross-origin requests
  - SSE (Server-Sent Events) support via sse-starlette

## Web Server

### Uvicorn
- **Version**: 0.32.0
- **Purpose**: ASGI server for running the FastAPI application
- **Usage**: Direct execution in `main.py` or via command line

## AI/ML Components

### LangChain
- **Versions**: 
  - langchain: >=0.3.4,<0.4.0
  - langchain-community: >=0.3.3,<0.4.0
  - langchain-chroma: 0.1.4
  - langchain-google-genai: 2.0.1
- **Purpose**: Framework for developing applications with large language models
- **Key Features Used**:
  - RAG (Retrieval-Augmented Generation) chain implementation
  - Integration with ChromaDB for vector storage
  - Integration with Google Gemini for LLM capabilities

### Google Generative AI
- **Version**: 0.8.3
- **Purpose**: Access to Google's Gemini models for natural language processing
- **Usage**: Backend LLM for chatbot responses

### ChromaDB
- **Version**: (Integrated via langchain-chroma)
- **Purpose**: Vector database for storing and retrieving document embeddings
- **Key Features Used**:
  - Document indexing and storage
  - Similarity search for RAG implementation

## Web Scraping

### Crawl4AI
- **Version**: >=0.3.1
- **Purpose**: Web crawling and content extraction for knowledge base enrichment
- **Usage**: Processing and indexing web content

## Data Processing

### PyPDF2
- **Purpose**: PDF document processing and text extraction
- **Usage**: Handling uploaded PDF files for indexing

### BeautifulSoup4
- **Version**: 4.12.3
- **Purpose**: HTML parsing for web content extraction
- **Usage**: Processing crawled web pages

### lxml
- **Version**: 5.3.0
- **Purpose**: XML and HTML processing library
- **Usage**: Supporting BeautifulSoup for web content parsing

## Configuration and Validation

### Pydantic
- **Version**: 2.9.2
- **Purpose**: Data validation and settings management
- **Usage**: 
  - Request/response data validation
  - Application settings management via `config.py`

### Pydantic Settings
- **Version**: >=2.5.2
- **Purpose**: Environment-based configuration management
- **Usage**: Loading configuration from `.env` file

## Utilities

### python-multipart
- **Version**: 0.0.12
- **Purpose**: Handling multipart/form-data requests
- **Usage**: Processing file uploads (PDFs)

### asyncio
- **Version**: 3.4.3
- **Purpose**: Asynchronous programming support
- **Usage**: Non-blocking operations throughout the application

### aiohttp
- **Version**: >=3.10.5
- **Purpose**: Asynchronous HTTP client/server
- **Usage**: Making async HTTP requests

### psutil
- **Purpose**: System and process utilities
- **Usage**: System monitoring and resource management

## Database

### MongoDB
- **Driver**: motor (Async MongoDB driver for Python)
- **Purpose**: Storing user feedback and application data
- **Configuration**:
  - URI: Configured via environment variable
  - Database: zendalona (default)
  - Collection: feedback (default)

## Development and Deployment

### Python Version
- **Required**: >=3.13 (as specified in pyproject.toml)

### Docker
- **Base Image**: python:3.13
- **Purpose**: Containerization for consistent deployment
- **Exposed Port**: 8000 (though app runs on PORT from config, default 10000)

## Key Environment Variables

| Variable | Purpose | Default/Example |
|----------|---------|-----------------|
| chroma_db_path | Path to ChromaDB storage | ./chroma_db |
| gemini_api_key | Google Gemini API key | your_gemini_api_key_here |
| mongodb_uri | MongoDB connection string | mongodb://localhost:27017/ |
| PORT | Application port | 10000 |

## Project Structure

The application follows a modular structure with:
- `main.py`: Application entry point
- `routers/`: API route definitions
- `utils/`: Utility functions and integrations
- `crawler/`: Web crawling functionality

## Running the Application

1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: Copy `.env.example` to `.env` and update values
3. Run application: `python main.py` or `uvicorn main:app --host 0.0.0.0 --port 10000`