from src.backend.services.embedding.embedder import EmbeddingService

def test_embed_empty():
    service = EmbeddingService()
    assert service.embed([]) == [] 