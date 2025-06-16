from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from backend.services.search.searcher import SearchService

router = APIRouter()
searcher = SearchService()

class SearchRequest(BaseModel):
    embedding: List[float]
    top_k: int = 5

@router.post("/search", response_model=List[Dict])
def search_chunks(request: SearchRequest):
    try:
        results = searcher.search(request.embedding, top_k=request.top_k)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 