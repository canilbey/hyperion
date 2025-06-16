from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from backend.services.embedding.embedder import EmbeddingService

router = APIRouter()
embedder = EmbeddingService()

class Chunk(BaseModel):
    content: str
    title: str = 'Untitled'
    order: int = 0
    metadata: Dict = {}

@router.post("/embed", response_model=List[Dict])
def embed_chunks(chunks: List[Chunk]):
    try:
        chunk_dicts = [c.dict() for c in chunks]
        embeddings = embedder.embed(chunk_dicts)
        # Embedding numpy array'i list'e çevrilir
        for emb in embeddings:
            if hasattr(emb['embedding'], 'tolist'):
                emb['embedding'] = emb['embedding'].tolist()
        return embeddings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 