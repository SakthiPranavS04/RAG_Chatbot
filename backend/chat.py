import logging
import os
from document_service import get_store
from config import settings
from google import genai
from google.genai import types

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
            
        prompt = f"""You are an AI assistant.
Answer ONLY using the provided documents context.
If the answer is unavailable, say "I could not find that information in the uploaded documents."
Never hallucinate.

Documents:
{context}

Question:
{question}
"""
        
        logger.info(f"Sending prompt to Gemini cloud model...")
        
        # Initialize Gemini Client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Call Gemini Model
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0
            )
        )
        
        answer = response.text
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
