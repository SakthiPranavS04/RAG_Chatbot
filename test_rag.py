import sys
from utils import get_vector_database

try:
    db = get_vector_database()
    docs = db.similarity_search("skills and projects")
    print(f"Found {len(docs)} documents.")
    for i, doc in enumerate(docs):
        print(f"Doc {i}: {doc.page_content[:100]}")
except Exception as e:
    print(f"Error: {e}")
