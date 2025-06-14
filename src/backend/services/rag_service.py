from backend.services.embedding_service import EmbeddingService
from backend.services.milvus_service import MilvusService
from backend.services.core.init_service import get_db
from typing import List, Dict
import re
import json

class RagService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.milvus_service = MilvusService()

    async def retrieve_context(self, query: str, top_k: int = 5, similarity_threshold: float = 0.1) -> List[Dict]:
        # Preprocessing uygula
        query_proc = self.embedding_service.preprocess(query)
        query_emb = self.embedding_service.embed([query_proc])[0]
        results = self.milvus_service.search(query_emb, top_k=top_k, similarity_threshold=similarity_threshold)
        context_chunks = []
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Database connection'ı al
        db = get_db()
        
        for hit in results[0]:
            # Metadata JSON olarak parse et
            metadata = None
            if hasattr(hit, 'entity') and hit.entity:
                metadata_str = hit.entity.get('metadata', '')
            elif hasattr(hit, 'metadata'):
                metadata_str = hit.metadata
            else:
                metadata_str = ''
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
            except Exception:
                metadata = {"raw": metadata_str}
            # Text'i ve diğer alanları al
            text_content = None
            if metadata and 'file_id' in metadata and 'chunk_index' in metadata:
                try:
                    query_text = """
                    SELECT text FROM text_chunks 
                    WHERE file_id = :file_id AND chunk_index = :chunk_index
                    """
                    result = await db.fetch_one(query_text, {"file_id": metadata['file_id'], "chunk_index": metadata['chunk_index']})
                    if result:
                        text_content = result["text"]
                        logger.info(f"Retrieved text content: {text_content[:100]}...")
                except Exception as e:
                    logger.error(f"Error retrieving text content: {e}")
            if not text_content and metadata and 'text' in metadata:
                text_content = metadata['text']
            score = getattr(hit, 'distance', None)
            if text_content:
                logger.info(f"RAG chunk: score={score}, text={text_content[:100]}...")
            else:
                logger.info(f"RAG chunk: score={score}, text=[NO TEXT], metadata={metadata}")
            context_chunks.append({
                "id": getattr(hit, 'id', None),
                "score": score,
                "text": text_content,
                "metadata": metadata
            })
        return context_chunks

    def assemble_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        # Bağlam olarak chunk['text'] kullan
        context_text = "\n".join([chunk["text"] for chunk in context_chunks if chunk["text"]])
        prompt = f"Soru: {query}\n\nBağlam:\n{context_text}\n\nYanıt:"
        return prompt 