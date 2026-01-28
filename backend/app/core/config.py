"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Cornell Notes Generator"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/cornell.db"
    
    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["pptx", "pdf", "docx", "png", "jpg", "jpeg"]
    
    # Processing
    OCR_TIMEOUT: int = 300  # 5 minutes per file
    MAX_CONCURRENT_GENERATIONS: int = 2
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Tesseract
    TESSDATA_PREFIX: str = "/usr/share/tesseract-ocr/5/tessdata/"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
