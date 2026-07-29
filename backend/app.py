import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest, ChatResponse, UploadResponse
from document_service import process_and_store_document
from chat import chat_with_documents

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI RAG Document Chatbot",
    description="API for uploading documents and chatting with them using RAG",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """
    Purpose: Health endpoint to verify the API is running.
    Input: None
    Output: JSON status
    """
    return {"status": "healthy"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Purpose: Upload a file (PDF, CSV, Excel, PPT), extract text/OCR, chunk, embed, and store in vector DB.
    Input: UploadFile object
    Output: UploadResponse with success message and chunk count
    """
    logger.info(f"Received file upload request: {file.filename}")
    
    # Validate extension
    allowed_extensions = {"pdf", "csv", "xls", "xlsx", "ppt", "pptx"}
    ext = file.filename.split(".")[-1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}")
        
    try:
        content = await file.read()
        
        # Limit upload size (e.g., 50MB)
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB.")
            
        chunks_processed = process_and_store_document(content, file.filename)
        
        return UploadResponse(
            filename=file.filename,
            message="File processed and stored successfully",
            chunks_processed=chunks_processed
        )
    except Exception as e:
        logger.error(f"Error processing file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Purpose: Answer questions based on uploaded documents.
    Input: ChatRequest containing the user's question
    Output: ChatResponse containing the answer and source citations
    """
    logger.info(f"Received chat request: {request.question}")
    try:
        response = chat_with_documents(request.question)
        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
