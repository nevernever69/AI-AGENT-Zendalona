# Zendalona Chatbot Backend Documentation

## Overview
This documentation provides a comprehensive overview of the Zendalona Chatbot backend architecture, core components, and file structure.

## Documentation Files

### 1. Architecture Documentation
- **File**: `ARCHITECTURE.md`
- **Content**: 
  - High-level system architecture
  - Component interaction diagrams
  - Data flow explanations
  - Key features overview

### 2. Core Code Snippets
- **File**: `CORE_SNIPPETS.md`
- **Content**:
  - Essential code examples
  - Key function implementations
  - Design pattern explanations
  - Performance optimization techniques

### 3. File Structure
- **File**: `FILE_STRUCTURE.md`
- **Content**:
  - Complete directory structure
  - Component descriptions
  - Module relationships
  - Dependency overview

## Key Components

### Main Application
- **Entry Point**: `main.py`
- **Configuration**: `config.py`
- **Data Models**: `utils/models.py`

### Core Routers
- **Chat**: `routers/chat.py` (Primary chat functionality)
- **Indexing**: `routers/indexing.py` (Document indexing)
- **Cache**: `routers/cache.py` (Cache management)
- **Feedback**: `routers/feedback.py` (User feedback)

### Utility Modules
- **LangChain Integration**: `utils/langchain_utils.py`
- **Vector Database**: `utils/chroma_utils.py`
- **Caching**: `utils/cache_utils.py`
- **Database**: `utils/mongo_utils.py`

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Application**:
   ```bash
   python main.py
   ```

## Development Guidelines

1. **Code Structure**: Follow the existing modular structure
2. **Documentation**: Update relevant documentation files when making changes
3. **Testing**: Ensure all changes are properly tested
4. **Configuration**: Use environment variables for configuration

## Additional Resources

- **API Documentation**: Available at `/docs` when running
- **Environment Template**: `.env.example`
- **Docker Configuration**: `Dockerfile`
- **Dependencies**: `requirements.txt`, `pyproject.toml`

For detailed information about any specific component, refer to the individual documentation files listed above.