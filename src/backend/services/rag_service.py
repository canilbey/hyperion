from backend.services.embedding_service import EmbeddingService
from backend.services.milvus_service import MilvusService
from backend.services.core.init_service import get_db
from typing import List, Dict
import re

class RagService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.milvus_service = MilvusService()

    async def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        query_emb = self.embedding_service.embed([query])[0]
        results = self.milvus_service.search(query_emb, top_k=top_k)
        context_chunks = []
        
        import logging
        logger = logging.getLogger(__name__)
        
        # Database connection'ı al
        db = get_db()
        
        for hit in results[0]:
            # Metadata'dan file_id ve chunk_index'i çıkar
            metadata = ""
            if hasattr(hit, 'entity') and hit.entity:
                metadata = hit.entity.get('metadata', '')
            elif hasattr(hit, 'metadata'):
                metadata = hit.metadata
            
            # Metadata'dan file_id ve chunk_index parse et
            # Format: "file:6d79a9d8-19c6-4902-a255-a13441887006:chunk:2:filename:test-document.txt"
            text_content = metadata  # Fallback
            if metadata:
                match = re.search(r'file:([^:]+):chunk:(\d+)', metadata)
                if match:
                    file_id = match.group(1)
                    chunk_index = int(match.group(2))
                    
                    # PostgreSQL'den asıl text içeriğini çek
                    try:
                        query_text = """
                        SELECT text FROM text_chunks 
                        WHERE file_id = :file_id AND chunk_index = :chunk_index
                        """
                        result = await db.fetch_one(query_text, {"file_id": file_id, "chunk_index": chunk_index})
                        if result:
                            text_content = result["text"]
                            logger.info(f"Retrieved text content: {text_content[:100]}...")
                        else:
                            logger.warning(f"No text found for file_id={file_id}, chunk_index={chunk_index}")
                    except Exception as e:
                        logger.error(f"Error retrieving text content: {e}")
            
            context_chunks.append({
                "id": hit.id,
                "score": hit.distance,
                "metadata": text_content  # Asıl text içeriği
            })
        return context_chunks

    def assemble_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        # Basit bir context birleştirme örneği
        context_text = "\n".join([chunk["metadata"] for chunk in context_chunks])
        prompt = f"Soru: {query}\n\nBağlam:\n{context_text}\n\nYanıt:"
        return prompt 