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
    UPLOAD_DIR: str = "uploads"
    CHROMA_DIR: str = "chroma_db"
    TESSERACT_PATH: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OLLAMA_BASE_URL: str = "https://ollama.com"
    OLLAMA_MODEL: str = "gpt-oss:120b-cloud"
    OLLAMA_API_KEY: str = ""

    class Config:
        env_file = _ENV_FILES or ".env"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
