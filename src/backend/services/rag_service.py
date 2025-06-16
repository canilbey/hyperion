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

    async def retrieve_context(self, query: str, similarity_threshold: float = 0.1, top_k: int = 5) -> List[Dict]:
        # Preprocessing uygula
        query_proc = self.embedding_service.preprocess(query)
        query_emb = self.embedding_service.embed([query_proc])[0]
        # Child chunk'larda arama yap
        results = self.milvus_service.search(query_emb, top_k=top_k, similarity_threshold=similarity_threshold)
        context_chunks = []
        import logging
        logger = logging.getLogger(__name__)
        # Database connection'ı al
        db = get_db()
        parent_ids = set()
        child_to_parent = {}
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
            parent_id = metadata.get('parent_id')
            if parent_id:
                parent_ids.add(parent_id)
                child_to_parent[hit.id] = parent_id
            score = getattr(hit, 'distance', None)
            context_chunks.append({
                "id": getattr(hit, 'id', None),
                "score": score,
                "metadata": metadata
            })
        # Parent chunk'ları veritabanından çek
        parent_chunks = {}
        if parent_ids:
            query_text = f"""
            SELECT id, title, content FROM parent_chunks WHERE id = ANY(:parent_ids)
            """
            result = await db.fetch_all(query_text, {"parent_ids": list(parent_ids)})
            for row in result:
                parent_chunks[row["id"]] = {
                    "title": row["title"],
                    "content": row["content"]
                }
        # Her child için parent chunk'ı bağlam olarak ekle
        final_context = []
        for chunk in context_chunks:
            parent_id = chunk["metadata"].get("parent_id")
            parent = parent_chunks.get(parent_id)
            if parent:
                final_context.append({
                    "child_id": chunk["id"],
                    "score": chunk["score"],
                    "parent_id": parent_id,
                    "parent_title": parent["title"],
                    "parent_content": parent["content"],
                    "child_metadata": chunk["metadata"]
                })
        return final_context

    def assemble_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        # Bağlam olarak chunk['text'] kullan
        context_text = "\n".join([chunk["text"] for chunk in context_chunks if chunk["text"]])
        prompt = f"Soru: {query}\n\nBağlam:\n{context_text}\n\nYanıt:"
        return prompt 