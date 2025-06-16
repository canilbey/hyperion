from src.backend.services.search.searcher import SearchService

def test_search_empty():
    service = SearchService()
    assert service.search(None) == [] 