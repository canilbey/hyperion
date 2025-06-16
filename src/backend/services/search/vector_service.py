def vector_search(query_embedding, milvus_client, top_k=10):
    """
    Milvus'ta vektör arama yap.
    """
    results = milvus_client.search(query_embedding, top_k=top_k)
    return results 