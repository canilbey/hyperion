def rerank_with_cross_encoder(query, candidates, cross_encoder_model, top_k=10):
    """
    Sonuçları cross-encoder ile yeniden sırala.
    """
    pairs = [(query, c['content']) for c in candidates]
    scores = cross_encoder_model.predict(pairs)
    reranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:top_k]
    return [c for c, s in reranked] 