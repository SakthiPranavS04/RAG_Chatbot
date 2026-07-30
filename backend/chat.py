import logging
import os
from document_service import get_store
from config import settings
import requests

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
            
        ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        model_name = settings.LLM_MODEL
        
        prompt = f"""You are an AI assistant.
Answer ONLY using the provided documents context.
If the answer is unavailable, say "I could not find that information in the uploaded documents."
Never hallucinate.

Documents:
{context}

Question:
{question}
"""
        
        logger.info(f"Sending prompt to Ollama model {model_name}...")
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        resp = requests.post(ollama_url, json=payload)
        resp.raise_for_status()
        
        data = resp.json()
        answer = data.get("response", "")
        
        return {
            "answer": answer,
            "sources": sources
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ollama API connection error: {str(e)}")
        raise Exception(f"Failed to connect to Ollama. Is it running at {settings.OLLAMA_BASE_URL} with model {settings.LLM_MODEL}?")
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
