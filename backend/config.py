import os
from pydantic_settings import BaseSettings

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_BASE_DIR)
_ENV_FILES = tuple(
    path for path in (
        os.path.join(_PROJECT_ROOT, ".env"),
        os.path.join(_BASE_DIR, ".env"),
    )
    if os.path.exists(path)
)

class Settings(BaseSettings):
    UPLOAD_FOLDER: str = "uploads"
    CHROMA_PATH: str = "chroma_db"
    TESSERACT_CMD: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    LLM_MODEL: str = "gpt-oss:20b-cloud"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = _ENV_FILES or ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(settings.CHROMA_PATH, exist_ok=True)
