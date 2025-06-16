from . import bm25_service, vector_service, fusion, rerank

def hybrid_search(query, bm25_index, milvus_client, cross_encoder_model, top_k=10):
    """
    Hibrit arama pipeline'ı: BM25 + vektör + fusion + reranking.
    """
    bm25_results = bm25_service.bm25_search(query, bm25_index, top_k=top_k)
    vector_results = vector_service.vector_search(query, milvus_client, top_k=top_k)
    fused = fusion.fuse_results(bm25_results, vector_results, top_k=top_k)
    # Fused sonuçlarda content alanı yoksa, DB'den çekilmeli
    # Burada örnek olarak candidates = fused
    reranked = rerank.rerank_with_cross_encoder(query, fused, cross_encoder_model, top_k=top_k)
    return reranked 