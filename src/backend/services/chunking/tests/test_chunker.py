from src.backend.services.chunking.chunker import ChunkingService

def test_chunk_empty():
    service = ChunkingService()
    assert service.chunk([]) == [] 