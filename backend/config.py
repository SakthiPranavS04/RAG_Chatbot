import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b-cloud")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "mxbai-embed-large")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "chroma_db")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

    # Text Splitting configs
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200

    # Retrieval configs
    TOP_K = 5

config = Config()
