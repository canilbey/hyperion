from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from backend.services.chunking.chunker import ChunkingService

router = APIRouter()
chunker = ChunkingService()

class Element(BaseModel):
    text: str
    # Gerekirse ek metadata

@router.post("/chunk", response_model=List[Dict])
def chunk_elements(elements: List[Element]):
    try:
        # Elementleri dict'e çevir
        element_dicts = [e.dict() for e in elements]
        chunks = chunker.chunk(element_dicts)
        return chunks
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 