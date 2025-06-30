from backend.services.embedding_service import EmbeddingService
from backend.services.milvus_service import MilvusService
from backend.services.core.init_service import get_db
from typing import List, Dict, Tuple
import re
import json
import logging

class RagService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.milvus_service = MilvusService()
        self.logger = logging.getLogger(__name__)

    def _extract_metadata(self, hit) -> Tuple[dict, str, float]:
        """Milvus hit'inden metadata, parent_id ve similarity score çıkarır"""
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
        score = getattr(hit, 'similarity', None)
        
        return metadata, parent_id, score

    def _get_unique_parent_chunks(self, hits, threshold: float = 0.1, max_parents: int = 2) -> List[str]:
        """
        Verilen hit'lerden benzersiz parent_id'leri döndürür.
        - threshold üzerindeki tüm değerleri kontrol eder
        - Ortak parent_id'leri engeller
        - max_parents sayısına ulaşana kadar devam eder
        """
        # Score'a göre sırala
        scored_hits = []
        for hit in hits:
            _, parent_id, score = self._extract_metadata(hit)
            if parent_id and score is not None:
                scored_hits.append((score, parent_id, hit))
        
        scored_hits.sort(reverse=True)  # En yüksek score'dan başla
        
        selected_parents = set()
        selected_hits = []
        
        # Önce threshold üstündeki tüm değerleri kontrol et
        for score, parent_id, hit in scored_hits:
            if score >= threshold and parent_id not in selected_parents:
                selected_parents.add(parent_id)
                selected_hits.append((score, parent_id, hit))
                
        # Eğer yeterli sayıda unique parent bulunamadıysa, devam et
        if len(selected_parents) < max_parents:
            for score, parent_id, hit in scored_hits:
                if parent_id not in selected_parents:
                    selected_parents.add(parent_id)
                    selected_hits.append((score, parent_id, hit))
                    if len(selected_parents) >= max_parents:
                        break
        
        return selected_hits

    async def retrieve_context(self, query: str) -> List[Dict]:
        """
        İki aşamalı retrieval pipeline:
        1. İlk 5 sonuç içinde:
           - 0.12 üzerindeki tüm değerler için retrieval
           - 0.12 üzerinde değer yoksa, 0.1 üzerindeki en iyi 2 değer (farklı parent'lardan)
        2. Ortak parent kontrolü:
           - Seçilen değerlerin parent'ları ortaksa, bir sonraki en yüksek değere geç
           - Benzersiz parent bulunana kadar devam et
        """
        query_proc = self.embedding_service.preprocess(query)
        query_emb = self.embedding_service.embed([query_proc])[0]
        
        # İlk 5 sonuç
        results_5 = self.milvus_service.search(query_emb, top_k=5)
        
        # 0.12 threshold için kontrol
        high_quality_hits = self._get_unique_parent_chunks(
            results_5[0], 
            threshold=0.12,
            max_parents=5  # 0.12 üzerindeki tüm değerler
        )
        
        # Eğer 0.12 üzerinde değer yoksa, 0.1 threshold ile dene
        if not high_quality_hits:
            high_quality_hits = self._get_unique_parent_chunks(
                results_5[0],
                threshold=0.1,
                max_parents=2  # En iyi 2 farklı parent
            )
        
        # Seçilen parent'ları logla
        for score, parent_id, _ in high_quality_hits:
            self.logger.info(f"[RAG] Seçilen parent_id: {parent_id}, similarity: {score}")
        
        # Parent chunk'ları veritabanından çek
        db = get_db()
        parent_chunks = {}
        
        if high_quality_hits:
            selected_parent_ids = [hit[1] for hit in high_quality_hits]  # (score, parent_id, hit)
            query_text = """
            SELECT id, title, content FROM parent_chunks WHERE id = ANY(:parent_ids)
            """
            result = await db.fetch_all(query_text, {"parent_ids": selected_parent_ids})
            for row in result:
                parent_chunks[row["id"]] = {
                    "title": row["title"],
                    "content": row["content"]
                }
        
        # Sonuçları hazırla
        final_context = []
        for _, parent_id, _ in high_quality_hits:
            if parent_id in parent_chunks:
                final_context.append({
                    "parent_id": parent_id,
                    "parent_title": parent_chunks[parent_id]["title"],
                    "parent_content": parent_chunks[parent_id]["content"]
                })
        
        return final_context

    def assemble_prompt(self, query: str, context_chunks: List[Dict]) -> str:
        # Bağlam olarak chunk['text'] kullan
        context_text = "\n".join([chunk["text"] for chunk in context_chunks if chunk["text"]])
        prompt = f"Soru: {query}\n\nBağlam:\n{context_text}\n\nYanıt:"
        return prompt 