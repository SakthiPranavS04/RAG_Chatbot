import logging
import re
from collections import Counter
import requests

from document_service import get_store
from config import settings

def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

def get_top_chunks(question, all_chunks, top_k=5):
    q_words = set(re.findall(r'\w+', question.lower()))
    stopwords = {"what", "is", "the", "a", "an", "of", "and", "in", "to", "how", "why", "can", "you", "summarize", "key", "points", "this", "file", "document", "documents", "are", "do", "does", "did", "please", "me", "tell", "about", "from"}
    q_words = q_words - stopwords
    
    if not q_words or not all_chunks:
        return all_chunks[:top_k]
        
    scored_chunks = []
    for chunk in all_chunks:
        chunk_words = re.findall(r'\w+', chunk.lower())
        chunk_word_counts = Counter(chunk_words)
        score = sum(chunk_word_counts.get(w, 0) for w in q_words)
        scored_chunks.append((score, chunk))
        
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [c for score, c in scored_chunks[:top_k]]

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
            
        all_chunks = []
        sources = []
        for filename, text in store.items():
            file_chunks = chunk_text(text)
            for i, chunk in enumerate(file_chunks):
                all_chunks.append(f"--- Document: {filename} (Part {i+1}) ---\n{chunk}\n")
            sources.append({
                "filename": filename,
                "page": 1,
                "chunk_id": f"{filename}_all"
            })
            
        top_chunks = get_top_chunks(question, all_chunks, top_k=5)
        context = "\n".join(top_chunks)
        
        system_prompt = """You are an AI assistant.
Answer ONLY using the provided documents context.
If the answer is unavailable, say "I could not find that information in the uploaded documents."
Never hallucinate."""

        prompt = f"""Documents Context (Top relevant excerpts):
{context}

Question:
{question}
"""
        
        if not settings.OLLAMA_BASE_URL:
            return {
                "answer": "Ollama base URL is missing. Please add it to your .env file.",
                "sources": sources
            }
            
        logger.info(f"Sending prompt to Ollama model: {settings.LLM_MODEL}")
        
        try:
            payload = {
                "model": settings.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }
            response = requests.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            answer = data.get("message", {}).get("content", "")
        except requests.RequestException as re:
            logger.error(f"Ollama API Error: {str(re)}")
            return {
                "answer": f"Ollama API Error: {str(re)}. Please check your Ollama server.",
                "sources": sources
            }
        
        if not answer:
            answer = "I could not generate a response from the model. Please try again."
            
        logger.info(f"Ollama response received from {settings.LLM_MODEL}")

        return {
            "answer": answer.strip(),
            "sources": sources
        }

    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
