import logging
import re
from collections import Counter

from document_service import get_store
from config import settings
from google import genai

FALLBACK_GEMINI_MODELS = (
    "gemini-flash-latest",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash-lite",
)

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

def _gemini_models_to_try():
    models = [settings.GEMINI_MODEL, *FALLBACK_GEMINI_MODELS]
    seen = set()
    ordered = []
    for model in models:
        if model and model not in seen:
            seen.add(model)
            ordered.append(model)
    return ordered

def _extract_response_text(response) -> str:
    if response.text:
        return response.text.strip()

    for candidate in getattr(response, "candidates", []) or []:
        parts = getattr(getattr(candidate, "content", None), "parts", None) or []
        text_parts = [part.text for part in parts if getattr(part, "text", None)]
        if text_parts:
            return "\n".join(text_parts).strip()

    return "I could not generate a response from the cloud model. Please try again."

def _generate_with_gemini(client, prompt: str):
    last_error = None
    for model in _gemini_models_to_try():
        try:
            logger.info(f"Sending prompt to Gemini cloud model: {model}")
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            answer = _extract_response_text(response)
            if answer:
                return answer, model
        except Exception as e:
            last_error = e
            error_msg = str(e)
            logger.warning(f"Gemini model {model} failed: {error_msg}")
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                continue
            if "404" in error_msg or "NOT_FOUND" in error_msg:
                continue
            raise

    if last_error:
        error_msg = str(last_error)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            raise Exception(
                "Gemini API quota exceeded for the configured cloud models. "
                "Please wait a minute and try again, or update GEMINI_MODEL in your .env file."
            )
        raise last_error

    raise Exception("No Gemini cloud models are available for this API key.")

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
        
        prompt = f"""You are an AI assistant.
Answer ONLY using the provided documents context.
If the answer is unavailable, say "I could not find that information in the uploaded documents."
Never hallucinate.

Documents Context (Top relevant excerpts):
{context}

Question:
{question}
"""
        
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            return {
                "answer": "GEMINI_API_KEY is not set in the environment (.env file). Please set it and restart the server.",
                "sources": []
            }

        client = genai.Client(api_key=api_key)
        answer, model_used = _generate_with_gemini(client, prompt)
        logger.info(f"Gemini cloud response received from {model_used}")

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
