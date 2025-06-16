def fuse_results(bm25_results, vector_results, weight_bm25=0.5, weight_vector=0.5, top_k=10):
    """
    BM25 ve vektör arama sonuçlarını skor ağırlıklandırması ile birleştir.
    """
    # Basit skor birleştirme örneği (id bazlı)
    fused = {}
    for res in bm25_results:
        fused[res['id']] = weight_bm25 * res['score']
    for res in vector_results:
        if res['id'] in fused:
            fused[res['id']] += weight_vector * res['score']
        else:
            fused[res['id']] = weight_vector * res['score']
    # Skora göre sırala ve top_k döndür
    sorted_results = sorted(fused.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{'id': rid, 'score': score} for rid, score in sorted_results] 