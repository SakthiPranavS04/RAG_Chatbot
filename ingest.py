import os
import shutil
from utils import load_and_split_documents, build_vector_database, DATA_DIR, CHROMA_DB_DIR

def main():
    print("Starting the data ingestion process...")
    
    # Check if the data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Error: The directory '{DATA_DIR}' does not exist. Please create it and add PDF files.")
        return
        
    # Check for supported files
    supported_extensions = ('.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg')
    data_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith(supported_extensions)]
    if not data_files:
        print(f"Warning: No supported files found in '{DATA_DIR}'. Please add some files and try again.")
        return
        
    print(f"Found {len(data_files)} file(s) in '{DATA_DIR}'.")
    
    from langchain_chroma import Chroma
    from utils import get_embedding_model
    
    existing_sources = set()
    db = None
    
    # Check what is already in the database
    if os.path.exists(CHROMA_DB_DIR):
        try:
            db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=get_embedding_model())
            res = db.get(include=['metadatas'])
            existing_sources = set([meta.get('source') for meta in res['metadatas'] if meta and 'source' in meta])
            print(f"Found {len(existing_sources)} unique file(s) already in the database.")
        except Exception as e:
            print(f"Could not read existing database: {e}")
            
    current_file_paths = set([os.path.join(DATA_DIR, f) for f in data_files])
    
    # 1. Delete removed files
    if db:
        sources_to_delete = existing_sources - current_file_paths
        if sources_to_delete:
            print(f"Deleting {len(sources_to_delete)} removed file(s) from database...")
            ids_to_delete = []
            for idx, meta in zip(res['ids'], res['metadatas']):
                if meta and meta.get('source') in sources_to_delete:
                    ids_to_delete.append(idx)
            if ids_to_delete:
                db.delete(ids=ids_to_delete)
                
    # 2. Find new files to ingest
    new_files = []
    for f in data_files:
        if os.path.join(DATA_DIR, f) not in existing_sources:
            new_files.append(f)
            
    if not new_files:
        print("Knowledge base is already up to date! No new files to process.")
        return
        
    print(f"Found {len(new_files)} new file(s) to process: {new_files}")
    
    # Extract and split chunks for NEW files only
    print("Loading and splitting new files into chunks...")
    try:
        chunks = load_and_split_documents(DATA_DIR, specific_files=new_files)
        
        if not chunks:
            print("Warning: Could not extract text from the new files.")
            return
            
        print(f"Successfully extracted {len(chunks)} text chunks.")
    except Exception as e:
        print(f"Error reading files: {e}")
        return
        
    # Build database
    print("Generating embeddings and adding to ChromaDB...")
    try:
        build_vector_database(chunks)
        print(f"Knowledge base updated successfully at '{CHROMA_DB_DIR}'.")
    except Exception as e:
        print(f"Error updating vector database: {e}")
        return

if __name__ == "__main__":
    main()
