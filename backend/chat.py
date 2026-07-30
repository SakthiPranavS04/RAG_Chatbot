import logging
import os
from document_service import get_store
from google import genai
from config import settings

logger = logging.getLogger(__name__)

def chat_with_documents(question: str) -> dict:
    try:
        logger.info(f"Processing chat question: {question}")
        store = get_store()
        
        if not store:
            return {
                "answer": "No documents uploaded yet.",
                "sources": []
            }
            
        context = ""
        sources = []
        for filename, text in store.items():
            context += f"--- Document: {filename} ---\n{text}\n\n"
            sources.append({
                "filename": filename,
                "page": 1,
                "chunk_id": f"{filename}_all"
            })
            
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return {
                "answer": "GEMINI_API_KEY is not set in the environment (.env file). Please set it and restart the server.",
                "sources": []
            }
            
        client = genai.Client(api_key=api_key)
        
        prompt = f"""You are an AI assistant.
Answer ONLY using the provided documents context.
If the answer is unavailable, say "I could not find that information in the uploaded documents."
Never hallucinate.

Documents:
{context}

Question:
{question}
"""
        
        logger.info("Sending prompt to Gemini...")
        response = client.models.generate_content(
            model='gemma-4-26b-a4b-it',
            contents=prompt,
        )
        
        return {
            "answer": response.text,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
