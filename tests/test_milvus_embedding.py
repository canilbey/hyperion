import pytest
from backend.services.embedding_service import EmbeddingService
from backend.services.milvus_service import MilvusService
import time

def test_milvus_embedding_integration():
    # 1. Servisleri başlat
    embedding_service = EmbeddingService()
    milvus_service = MilvusService(collection_name="test_embeddings")

    # 2. Temiz bir koleksiyon ile başla (varsa sil)
    try:
        from pymilvus import utility
        if utility.has_collection("test_embeddings"):
            utility.drop_collection("test_embeddings")
    except Exception:
        pass

    # 3. Örnek metin ve embedding
    text = "Hyperion platformu belge tabanlı arama için geliştirilmiştir."
    embedding = embedding_service.embed([text])[0]
    metadata = "test-doc-1"

    # 4. Milvus'a ekle
    milvus_service.insert_embedding(embedding, metadata)
    time.sleep(1)  # Milvus'un indexlemesi için kısa bekleme

    # 5. Benzer bir metinle arama yap
    query = "Hyperion belge arama platformudur."
    query_embedding = embedding_service.embed([query])[0]
    results = milvus_service.search(query_embedding, top_k=3)

    # 6. Sonuçları kontrol et
    assert len(results) > 0
    found = False
    for hit in results[0]:
        if hasattr(hit, 'entity') and hit.entity.get('metadata', '') == metadata:
            found = True
            break
    assert found, "Eklenen embedding arama ile bulunamadı!" 