from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User question")

class SourceCitation(BaseModel):
    filename: str
    page: int
    chunk_id: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]

class DocumentInfo(BaseModel):
    filename: str
    document_type: str
    upload_time: str
    size: int

class DeleteRequest(BaseModel):
    filename: str
