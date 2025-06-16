def bm25_search(query, index, top_k=10):
    """
    BM25 arama motorunda sorgu yap. (Elasticsearch/Whoosh/benzeri ile uyumlu)
    """
    # index.search(query, top_k) gibi bir arayüz varsayalım
    results = index.search(query, top_k=top_k)
    return results 