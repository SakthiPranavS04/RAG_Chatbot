import os
import io
import time
import logging
from pypdf import PdfReader
from PIL import Image
import pytesseract
from pptx import Presentation
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from config import settings

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

# Initialize Embeddings
embeddings = OllamaEmbeddings(
    model=settings.EMBEDDING_MODEL,
    base_url=settings.OLLAMA_BASE_URL
)

# Initialize ChromaDB persistent client
vector_store = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory=settings.CHROMA_DIR
)

def chunk_text(text: str, metadata: dict) -> list:
    """
    Purpose: Split text into smaller chunks for embeddings.
    Input: Full text of a document/page, metadata dict
    Output: List of Langchain Document objects containing chunked text and metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.create_documents([text], metadatas=[metadata])
    # Add unique chunk_id to each chunk's metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{metadata['filename']}_p{metadata.get('page', 1)}_{i}"
    return chunks

def extract_text_from_pdf(file_path: str, filename: str) -> list:
    """
    Purpose: Extract text from PDF, applying OCR via Tesseract if page has no text.
    Input: file_path (str), filename (str)
    Output: list of Document chunks
    """
    chunks = []
    try:
        reader = PdfReader(file_path)
        upload_time = time.time()
        
        # pypdf currently does not easily expose get_pixmap for Tesseract fallback without pdf2image.
        # Since pdf2image is in our requirements, let's use it for the fallback OCR.
        from pdf2image import convert_from_path
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            # If no text found, perform OCR on the page
            if not text or not text.strip():
                logger.info(f"No text found on page {page_num + 1}, falling back to OCR...")
                # Extract image for this page (1-indexed for pdf2image)
                images = convert_from_path(file_path, first_page=page_num+1, last_page=page_num+1)
                if images:
                    img = images[0]
                    text = pytesseract.image_to_string(img)
            
            if text and text.strip():
                metadata = {
                    "filename": filename,
                    "page": page_num + 1,
                    "document_type": "pdf",
                    "upload_time": upload_time
                }
                chunks.extend(chunk_text(text, metadata))
                
    except Exception as e:
        logger.error(f"Failed to process PDF {filename}: {str(e)}")
        raise
    return chunks

import csv
import openpyxl

def extract_text_from_csv(file_path: str, filename: str) -> list:
    """
    Purpose: Extract text from CSV files by converting rows to text.
    Input: file_path (str), filename (str)
    Output: list of Document chunks
    """
    chunks = []
    try:
        upload_time = time.time()
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for idx, row in enumerate(reader):
                text = " ".join([f"{col}: {val}" for col, val in row.items() if val])
                if text.strip():
                    metadata = {
                        "filename": filename,
                        "page": idx + 1, # represent row as page
                        "document_type": "csv",
                        "upload_time": upload_time
                    }
                    chunks.extend(chunk_text(text, metadata))
    except Exception as e:
        logger.error(f"Failed to process CSV {filename}: {str(e)}")
        raise
    return chunks

def extract_text_from_excel(file_path: str, filename: str) -> list:
    """
    Purpose: Extract text from Excel files across all sheets.
    Input: file_path (str), filename (str)
    Output: list of Document chunks
    """
    chunks = []
    try:
        upload_time = time.time()
        wb = openpyxl.load_workbook(file_path, data_only=True)
        for sheet_name in wb.sheetnames:
            sheet = wb[sheet_name]
            # Assuming first row is header
            headers = [cell.value for cell in sheet[1]]
            
            for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True)):
                row_parts = []
                for h, val in zip(headers, row):
                    if val is not None:
                        row_parts.append(f"{h}: {val}")
                
                text = " ".join(row_parts)
                if text.strip():
                    metadata = {
                        "filename": filename,
                        "page": f"{sheet_name}_r{idx + 1}",
                        "document_type": "excel",
                        "upload_time": upload_time
                    }
                    chunks.extend(chunk_text(text, metadata))
    except Exception as e:
        logger.error(f"Failed to process Excel {filename}: {str(e)}")
        raise
    return chunks

def extract_text_from_ppt(file_path: str, filename: str) -> list:
    """
    Purpose: Extract text from PowerPoint files.
    Input: file_path (str), filename (str)
    Output: list of Document chunks
    """
    chunks = []
    try:
        prs = Presentation(file_path)
        upload_time = time.time()
        for i, slide in enumerate(prs.slides):
            text = ""
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
            if text.strip():
                metadata = {
                    "filename": filename,
                    "page": i + 1,
                    "document_type": "ppt",
                    "upload_time": upload_time
                }
                chunks.extend(chunk_text(text, metadata))
    except Exception as e:
        logger.error(f"Failed to process PPT {filename}: {str(e)}")
        raise
    return chunks

def process_and_store_document(file_content: bytes, filename: str) -> int:
    """
    Purpose: Main entry to process an uploaded document, embed it, and store in vector DB.
    Input: raw file content bytes, filename
    Output: number of chunks stored
    """
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file_content)
        
    ext = filename.split(".")[-1].lower()
    chunks = []
    
    logger.info(f"Processing uploaded file: {filename}")
    
    if ext == "pdf":
        chunks = extract_text_from_pdf(file_path, filename)
    elif ext == "csv":
        chunks = extract_text_from_csv(file_path, filename)
    elif ext in ["xls", "xlsx"]:
        chunks = extract_text_from_excel(file_path, filename)
    elif ext in ["ppt", "pptx"]:
        chunks = extract_text_from_ppt(file_path, filename)
    else:
        logger.error(f"Unsupported file type: {ext}")
        raise ValueError(f"Unsupported file type: {ext}")
        
    if not chunks:
        logger.warning(f"No text extracted from {filename}")
        raise ValueError(f"Could not extract text from {filename}")
        
    # Remove existing chunks for this file before inserting (simulates update)
    delete_document(filename)
        
    # Store in ChromaDB
    logger.info(f"Storing {len(chunks)} chunks in vector database for {filename}")
    vector_store.add_documents(documents=chunks)
    
    return len(chunks)

def retrieve_vectors(query: str, k: int = 5) -> list:
    """
    Purpose: Retrieve top K similar chunks from ChromaDB for a given query.
    Input: Search query, number of results (k)
    Output: list of Document chunks
    """
    logger.info(f"Retrieving top {k} documents for query: {query}")
    results = vector_store.similarity_search(query, k=k)
    return results

def delete_document(filename: str):
    """
    Purpose: Remove a document's vectors from ChromaDB by filename.
    Input: filename
    Output: None
    """
    try:
        logger.info(f"Deleting existing document vectors for: {filename}")
        # Search for document chunks and delete by id
        existing = vector_store.get(where={"filename": filename})
        if existing and existing["ids"]:
            vector_store.delete(ids=existing["ids"])
            logger.info(f"Deleted {len(existing['ids'])} chunks for {filename}")
    except Exception as e:
        logger.error(f"Failed to delete document {filename}: {str(e)}")
