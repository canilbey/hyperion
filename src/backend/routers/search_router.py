from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.search.searcher import SearchService
from backend.services.search.hybrid_search import hybrid_search
from backend.services.milvus_service import MilvusService
# BM25 index örneği için örnek: Whoosh veya benzeri bir arama motoru kullanılabilir
# from backend.services.search.bm25_index_loader import load_bm25_index

router = APIRouter()
searcher = SearchService()

# BM25 index örneği için örnek: Whoosh veya benzeri bir arama motoru kullanılabilir
# from backend.services.search.bm25_index_loader import load_bm25_index

bm25_index = None  # TODO: Uygun şekilde initialize et
milvus_client = None  # TODO: Uygun şekilde initialize et

class SearchRequest(BaseModel):
    embedding: List[float]
    top_k: int = 5

class HybridSearchRequest(BaseModel):
    query: str
    top_k: int = 10

@router.post("/search", response_model=List[Dict])
def search_chunks(request: SearchRequest):
    try:
        results = searcher.search(request.embedding, top_k=request.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search/hybrid", response_model=List[Dict])
def search_hybrid(request: HybridSearchRequest):
    try:
        # bm25_index, milvus_client, cross_encoder_model sistemde uygun şekilde alınmalı
        # Burada örnek olarak None geçiyoruz
        if bm25_index is None:
            return {"error": "BM25 index is not initialized!"}
        if milvus_client is None:
            return {"error": "Milvus client is not initialized!"}
        results = hybrid_search(request.query, bm25_index=bm25_index, milvus_client=milvus_client, cross_encoder_model=None, top_k=request.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 