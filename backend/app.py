import os
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from config import config
from models import ChatRequest, ChatResponse, DeleteRequest, DocumentInfo
from document_service import document_service
from chat import chat_service

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="AI-Powered Multi-Document RAG Chatbot API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    ext = file.filename.split(".")[-1].lower()
    allowed_exts = ["pdf", "csv", "xlsx", "xls"]
    
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Allowed: {', '.join(allowed_exts)}")
        
    # Check for duplicates in DB
    existing_docs = chat_service.get_documents()
    if any(doc["filename"] == file.filename for doc in existing_docs):
        raise HTTPException(status_code=400, detail="File already exists. Please delete it first or upload a different file.")

    file_path = os.path.join(config.UPLOAD_FOLDER, file.filename)
    
    try:
        # Save file securely
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # Process and extract text
        chunks = document_service.process_file(file_path, file.filename, ext)
        
        # Add to Vector Store
        chat_service.add_documents(chunks)
        
        return {"message": "File uploaded and processed successfully", "filename": file.filename, "chunks": len(chunks)}
        
    except Exception as e:
        logger.error(f"Error during upload of {file.filename}: {str(e)}")
        # Clean up file if failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = chat_service.chat(request.message)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate response")

@app.get("/documents", response_model=List[DocumentInfo])
def list_documents():
    try:
        return chat_service.get_documents()
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@app.post("/delete")
def delete_document(request: DeleteRequest):
    if not request.filename:
        raise HTTPException(status_code=400, detail="Filename required")
        
    try:
        chat_service.delete_document(request.filename)
        
        file_path = os.path.join(config.UPLOAD_FOLDER, request.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return {"message": f"{request.filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting {request.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
