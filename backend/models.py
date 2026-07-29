from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    question: str

class SourceCitation(BaseModel):
    filename: str
    page: int
    chunk_id: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]

class UploadResponse(BaseModel):
    filename: str
    message: str
    chunks_processed: int
