import logging
from typing import List
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from config import config
from models import SourceCitation
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        try:
            self.embeddings = OllamaEmbeddings(
                model=config.EMBEDDING_MODEL,
                base_url=config.OLLAMA_BASE_URL
            )
            
            self.llm = Ollama(
                model=config.OLLAMA_MODEL,
                base_url=config.OLLAMA_BASE_URL
            )
            
            # Persistent ChromaDB client
            self.chroma_client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
            
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name="documents",
                embedding_function=self.embeddings,
                persist_directory=config.CHROMA_DB_PATH
            )
            
            self.prompt_template = PromptTemplate(
                template="""You are an intelligent document assistant.

Answer ONLY from the retrieved context.

Never use outside knowledge.

If the answer cannot be found inside the retrieved context,
respond exactly:
"I could not find that information in the uploaded documents."

Always include source citations.

Context:
{context}

Question: {question}
Answer:""",
                input_variables=["context", "question"]
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatService: {str(e)}")
            raise

    def add_documents(self, documents: List):
        if not documents:
            return
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} chunks to vector store.")
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {str(e)}")
            raise

    def get_documents(self):
        try:
            collection = self.chroma_client.get_or_create_collection("documents")
            results = collection.get(include=['metadatas'])
            metadatas = results.get("metadatas", [])
            
            # Deduplicate by filename
            docs = {}
            for meta in metadatas:
                if meta and "filename" in meta:
                    fname = meta["filename"]
                    if fname not in docs:
                        docs[fname] = {
                            "filename": fname,
                            "document_type": meta.get("document_type", "Unknown"),
                            "upload_time": meta.get("upload_time", "0"),
                            "size": 0 # Size is handled at file level in app.py or we just leave it 0
                        }
            return list(docs.values())
        except Exception as e:
            logger.error(f"Failed to get documents: {str(e)}")
            return []

    def delete_document(self, filename: str):
        try:
            collection = self.chroma_client.get_or_create_collection("documents")
            collection.delete(where={"filename": filename})
            logger.info(f"Deleted {filename} from vector store.")
        except Exception as e:
            logger.error(f"Failed to delete document {filename}: {str(e)}")
            raise

    def chat(self, question: str) -> dict:
        try:
            docs = self.vector_store.similarity_search(question, k=config.TOP_K)
            
            if not docs:
                return {
                    "answer": "I could not find that information in the uploaded documents.",
                    "sources": []
                }
                
            context = "\n\n".join([f"Source: {doc.metadata.get('filename')} (Page {doc.metadata.get('page')})\n{doc.page_content}" for doc in docs])
            
            prompt = self.prompt_template.format(context=context, question=question)
            
            response = self.llm.invoke(prompt)
            
            # If the LLM somehow decides not to use the exact string, enforce it if context was irrelevant (though we rely on prompt for this mostly)
            # The prompt instructs it to say exactly that string.
            
            sources = []
            seen_chunks = set()
            for doc in docs:
                chunk_id = doc.metadata.get("chunk_id", "")
                if chunk_id not in seen_chunks:
                    sources.append(SourceCitation(
                        filename=doc.metadata.get("filename", "Unknown"),
                        page=doc.metadata.get("page", 0),
                        chunk_id=chunk_id
                    ))
                    seen_chunks.add(chunk_id)
            
            return {
                "answer": response.strip(),
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"Chat generation failed: {str(e)}")
            raise

chat_service = ChatService()
