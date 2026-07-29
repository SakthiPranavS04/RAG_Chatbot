import os
import pandas as pd
from PIL import Image
import pytesseract
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# -------------------------------------------------------------
# Configuration Constants
# -------------------------------------------------------------
DATA_DIR = "data"
CHROMA_DB_DIR = "chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"
CHAT_MODEL = "gpt-oss:20b-cloud"

def get_embedding_model():
    """
    Initializes the Ollama embedding model using the modern langchain-ollama package.
    """
    return OllamaEmbeddings(model=EMBEDDING_MODEL)

def get_chat_model():
    """
    Initializes the ChatOllama model using the modern langchain-ollama package.
    """
    return ChatOllama(model=CHAT_MODEL)

def load_and_split_documents(data_path=DATA_DIR, specific_files=None):
    """
    Loads various file types (PDF, Excel, Word, Images) and splits them into chunks.
    If specific_files is provided, only those filenames will be processed.
    """
    documents = []
    
    if not os.path.exists(data_path):
        return []

    for filename in os.listdir(data_path):
        if specific_files is not None and filename not in specific_files:
            continue
            
        file_path = os.path.join(data_path, filename)
        ext = filename.lower().split('.')[-1]
        
        try:
            if ext == 'pdf':
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif ext == 'docx':
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())
            elif ext == 'xlsx':
                # Read Excel using pandas and convert to text
                df = pd.read_excel(file_path)
                text = df.to_csv(index=False)
                documents.append(Document(page_content=text, metadata={"source": file_path}))
            elif ext in ['png', 'jpg', 'jpeg']:
                # Read Image using pytesseract
                try:
                    text = pytesseract.image_to_string(Image.open(file_path))
                    if text.strip():
                        documents.append(Document(page_content=text, metadata={"source": file_path}))
                    else:
                        print(f"Warning: No text found in image {filename}")
                except Exception as e:
                    print(f"Error processing image {filename}: {e}. Ensure Tesseract OCR is installed.")
        except Exception as e:
            print(f"Error loading {filename}: {e}")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    return chunks

def build_vector_database(chunks):
    """
    Generates embeddings for the chunks and persists them into ChromaDB.
    """
    embeddings = get_embedding_model()
    
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    
    return vector_db

def get_vector_database():
    """
    Loads the persistent ChromaDB database.
    """
    embeddings = get_embedding_model()
    
    vector_db = Chroma(
        persist_directory=CHROMA_DB_DIR, 
        embedding_function=embeddings
    )
    
    return vector_db

def format_docs(docs):
    """
    Helper function for LCEL to format the retrieved Document objects into a single string.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def generate_answer(query):
    """
    Uses LangChain Expression Language (LCEL) instead of deprecated Chains to execute RAG.
    Retrieves context, formats it, applies the prompt, queries the LLM, and parses the output.
    """
    vector_db = get_vector_database()
    llm = get_chat_model()
    
    # Retrieve top 15 relevant chunks to give more context for evaluations
    retriever = vector_db.as_retriever(search_kwargs={"k": 15})
    
    # Retrieve documents
    docs = retriever.invoke(query)
    context = format_docs(docs)
    
    # Modern Prompt formulation
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful AI assistant. Use the following context to answer the user's question. If you don't know the answer, say that you don't know. Keep your answer concise.\n\nContext: {context}"),
        ("human", "{question}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    # Execute chain
    answer = chain.invoke({"context": context, "question": query})
    
    # Extract unique sources (removing the 'data\' prefix if present)
    sources = set([doc.metadata.get("source", "Unknown") for doc in docs])
    
    return answer, sources
