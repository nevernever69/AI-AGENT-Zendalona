import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str  # Renamed from GOOGLE_API_KEY
    chroma_db_path: str = "chroma_db"
    log_path: str = "logs/app.log"
    crawler_depth: int = 2
    crawler_max_pages: int = 10
    document_store_path: str = "./document_store"  # Added new field
    PORT: int
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
