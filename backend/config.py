import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gpt-oss:20b-cloud"
    EMBEDDING_MODEL: str = "mxbai-embed-large"
    UPLOAD_DIR: str = "uploads"
    CHROMA_DIR: str = "chroma_db"
    TESSERACT_PATH: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
