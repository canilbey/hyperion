from backend.services.embedding_service import EmbeddingService
from backend.services.milvus_service import MilvusService
from typing import List, Dict

class RagService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.milvus_service = MilvusService()

    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        query_emb = self.embedding_service.embed([query])[0]
        results = self.milvus_service.search(query_emb, top_k=top_k)
        context_chunks = []
        for hit in results[0]:
            context_chunks.append({
                "id": hit.id,
                "score": hit.distance,
                "metadata": hit.entity.get('metadata', '')
            })
        return context_chunks

    def assemble_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        # Basit bir context birleştirme örneği
        context_text = "\n".join([chunk["metadata"] for chunk in context_chunks])
        prompt = f"Soru: {query}\n\nBağlam:\n{context_text}\n\nYanıt:"
        return prompt 