import logging
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from config import settings
from document_service import retrieve_vectors
from models import ChatResponse, SourceCitation

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOllama(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL
)

PROMPT_TEMPLATE = """You are an AI assistant.
Answer ONLY using the retrieved documents.
If the answer is unavailable,
say
"I could not find that information in the uploaded documents."
Never hallucinate.
Return citations.

Documents:
{context}

Question:
{question}
"""

prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

def chat_with_documents(question: str) -> ChatResponse:
    """
    Purpose: Receive a question, retrieve relevant chunks, generate an answer using the LLM, and format the response.
    Input: user question string
    Output: ChatResponse object with answer and sources
    """
    try:
        logger.info(f"Processing chat question: {question}")
        
        # 1. Retrieve chunks
        docs = retrieve_vectors(question, k=5)
        
        if not docs:
            return ChatResponse(
                answer="I could not find that information in the uploaded documents.",
                sources=[]
            )
            
        # 2. Prepare context and sources
        context = ""
        sources = []
        seen_chunks = set()
        
        for doc in docs:
            context += doc.page_content + "\n\n"
            meta = doc.metadata
            chunk_id = meta.get("chunk_id", "")
            if chunk_id not in seen_chunks:
                seen_chunks.add(chunk_id)
                sources.append(SourceCitation(
                    filename=meta.get("filename", "unknown"),
                    page=int(meta.get("page", 1)) if isinstance(meta.get("page"), (int, str)) and str(meta.get("page")).isdigit() else 1,
                    chunk_id=chunk_id
                ))
                
        # 3. Create prompt and call LLM
        formatted_prompt = prompt.format(context=context, question=question)
        logger.info("Sending prompt to LLM...")
        
        response = llm.invoke(formatted_prompt)
        
        return ChatResponse(
            answer=response.content,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise
