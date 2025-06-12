from pydantic_settings import BaseSettings
from pydantic import Extra
import dotenv

class Settings(BaseSettings):
    # Existing settings
    chroma_db_path: str
    log_path: str
    gemini_api_key: str
    crawler_depth: int
    crawler_max_pages: int
    document_store_path: str
    PORT: int = 8000

    # New MongoDB settings
    mongodb_uri: str = dotenv.mongodb_uri
    mongodb_database: str = "zendalona"
    mongodb_feedback_collection: str = "feedback"

    class Config:
        extra = Extra.allow
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()