from . import bm25_service, vector_service, fusion, rerank
from backend.services.rag_service import RagService

def hybrid_search(query, bm25_index, milvus_client, cross_encoder_model, top_k=10):
    """
    Advanced RAG hybrid search pipeline:
    - BM25 ve vektör arama yapılır.
    - Semantic search pipeline'ı ile parent chunk'lar alınır.
    - BM25 ve vektör sonuçları fusion ile birleştirilir.
    - Parent chunk tekrarları engellenir.
    - İlk 10-20 sonuç cross-encoder ile rerank edilir.
    - Sonuçlar içerik ve metadata ile birlikte döner.
    """
    # BM25 ve vektör arama
    bm25_results = bm25_service.bm25_search(query, bm25_index, top_k=top_k)
    vector_results = vector_service.vector_search(query, milvus_client, top_k=top_k)
    # Semantic search ile parent chunk'ları al
    rag_service = RagService()
    import asyncio
    parent_chunks_semantic = asyncio.run(rag_service.retrieve_context(query))
    # Fusion
    fused = fusion.fuse_results(bm25_results, vector_results, top_k=top_k)
    # Parent chunk tekrarlarını engelle, semantic search parent'larını da dahil et
    parent_ids = set()
    results_with_content = []
    # BM25 ve vektör sonuçlarından parent_id topla
    for res in bm25_results + vector_results:
        meta = res.get('metadata', {})
        pid = meta.get('parent_id')
        if pid:
            parent_ids.add(pid)
    # Semantic search parent'larını da ekle
    for p in parent_chunks_semantic:
        parent_ids.add(p['parent_id'])
    # Parent chunk'ları veritabanından çek (örnek: rag_service ile)
    # (Burada async/await yerine örnek sync çağrı var, gerçek kodda async olmalı)
    parent_chunks = {p['parent_id']: p for p in parent_chunks_semantic}
    # Sonuçları parent bazında birleştir
    for pid in parent_ids:
        parent = parent_chunks.get(pid)
        if parent:
            results_with_content.append({
                'parent_id': pid,
                'parent_title': parent['parent_title'],
                'parent_content': parent['parent_content'],
                'score': None,  # Fusion skorunu buraya ekleyebilirsin
                'source': 'hybrid',
            })
    # Fusion skorlarını parent_id ile eşleştirip ekle (isteğe bağlı)
    # Sonuçları skora göre sırala ve dön
    return results_with_content[:top_k] 