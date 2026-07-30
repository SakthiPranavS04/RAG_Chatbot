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

At the very end of your response, you MUST provide a list of the exact document filenames you used to answer the question, formatted exactly like this on a new line:
SOURCES: filename1, filename2

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
        
        answer_text = response.text
        used_filenames = []
        
        # Parse the SOURCES: line
        lines = answer_text.split('\n')
        final_answer_lines = []
        for line in lines:
            if line.strip().startswith("SOURCES:"):
                sources_str = line.strip().replace("SOURCES:", "").strip()
                if sources_str and sources_str.lower() != "none" and sources_str != "[]":
                    # Extract filenames
                    used_filenames = [s.strip() for s in sources_str.split(',') if s.strip()]
            else:
                final_answer_lines.append(line)
                
        final_answer = "\n".join(final_answer_lines).strip()
        
        # Filter sources to only include the ones the LLM cited
        final_sources = []
        for src in sources:
            if src["filename"] in used_filenames or not used_filenames: 
                # If LLM didn't return any sources format properly, fallback to all (or none, but let's just show the matched ones if any)
                pass
        
        # Actually let's strictly filter
        if used_filenames:
            final_sources = [s for s in sources if s["filename"] in used_filenames]
        else:
            final_sources = [] # Or 'sources' if we want fallback

        return {
            "answer": final_answer,
            "sources": final_sources
        }
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
