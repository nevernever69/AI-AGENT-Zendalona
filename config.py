from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    chroma_db_path: str = Field(default="chroma_db")
    log_path: str = Field(default="logs/app.log")
    crawler_depth: int = Field(default=2)
    crawler_max_pages: int = Field(default=10)
    document_store_path: str = Field(default="./document_store")

    mongo_url: str = Field(..., alias="MONGO_URL")

    # jwt_secret: str = Field(..., alias="JWT_SECRET")
    # jwt_expire_minutes: int = Field(default=60)  # default = 1 hour

    port: int = Field(..., alias="PORT")
    debug: bool = Field(default=False, alias="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True

settings = Settings()
