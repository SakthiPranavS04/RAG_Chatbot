import os
import time
import logging
import pandas as pd
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from config import config

# Ensure the upload folder exists
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# Set tesseract path
pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )

    def extract_text_from_pdf(self, file_path: str, filename: str) -> list[Document]:
        documents = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text("text")
                
                # If no text found, try OCR
                if not text.strip():
                    logger.info(f"No text found on page {page_num + 1} of {filename}. Attempting OCR.")
                    try:
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution for OCR
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        text = pytesseract.image_to_string(img)
                    except Exception as e:
                        logger.error(f"OCR failed on page {page_num + 1} of {filename}: {str(e)}")
                        continue

                if text.strip():
                    documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "filename": filename,
                                "page": page_num + 1,
                                "document_type": "PDF",
                                "upload_time": str(time.time())
                            }
                        )
                    )
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}")
            raise e
        return documents

    def extract_text_from_csv(self, file_path: str, filename: str) -> list[Document]:
        documents = []
        try:
            df = pd.read_csv(file_path)
            for index, row in df.iterrows():
                row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                documents.append(
                    Document(
                        page_content=row_text,
                        metadata={
                            "filename": filename,
                            "page": index + 1,
                            "document_type": "CSV",
                            "upload_time": str(time.time())
                        }
                    )
                )
        except Exception as e:
            logger.error(f"Error processing CSV {filename}: {str(e)}")
            raise e
        return documents

    def extract_text_from_excel(self, file_path: str, filename: str) -> list[Document]:
        documents = []
        try:
            # openpyxl for xlsx, xlrd might be needed for xls depending on pandas version
            df_dict = pd.read_excel(file_path, sheet_name=None)
            page_counter = 1
            for sheet_name, df in df_dict.items():
                for index, row in df.iterrows():
                    row_text = f"Sheet: {sheet_name} | " + ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                    documents.append(
                        Document(
                            page_content=row_text,
                            metadata={
                                "filename": filename,
                                "page": page_counter,
                                "document_type": "EXCEL",
                                "upload_time": str(time.time())
                            }
                        )
                    )
                    page_counter += 1
        except Exception as e:
            logger.error(f"Error processing Excel {filename}: {str(e)}")
            raise e
        return documents

    def process_file(self, file_path: str, filename: str, ext: str) -> list[Document]:
        if ext.lower() == 'pdf':
            docs = self.extract_text_from_pdf(file_path, filename)
        elif ext.lower() == 'csv':
            docs = self.extract_text_from_csv(file_path, filename)
        elif ext.lower() in ['xlsx', 'xls']:
            docs = self.extract_text_from_excel(file_path, filename)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        # Add chunk_id and split
        chunks = self.text_splitter.split_documents(docs)
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = f"{chunk.metadata['filename']}_p{chunk.metadata['page']}_c{i}"
            
        return chunks

document_service = DocumentService()
