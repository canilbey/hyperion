from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.embedding_service import EmbeddingService
from backend.services.milvus_service import MilvusService
from backend.services.rag_service import RagService
from backend.services.llm_service import LlmService
import logging

router = APIRouter()
embedding_service = EmbeddingService()
milvus_service = MilvusService()
rag_service = RagService()
llm_service = LlmService()
logger = logging.getLogger(__name__)

class EmbedRequest(BaseModel):
    texts: List[str]

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    id: int
    score: float
    metadata: str

class SearchResponse(BaseModel):
    results: List[SearchResult]

class RagRetrieveRequest(BaseModel):
    query: str
    top_k: int = 5

class RagRetrieveResponse(BaseModel):
    prompt: str
    context_chunks: List[SearchResult]

class RagCompleteRequest(BaseModel):
    query: str
    top_k: int = 5
    max_tokens: int = 256
    temperature: float = 0.2

class RagCompleteResponse(BaseModel):
    prompt: str
    context_chunks: List[SearchResult]
    answer: str

@router.post('/embed', response_model=EmbedResponse)
def embed_texts(request: EmbedRequest):
    """
    Purpose:
        Generate embeddings for a list of input texts.
    Usage:
        POST /embedding/embed
        Body: JSON with a single field 'texts' (list of strings)
    Role in the System:
        Provides vector representations for input texts, used in search and retrieval.
    Authentication/Authorization:
        No authentication required by default.
    Example Usage (cURL):
        curl -X POST "http://localhost:8000/embedding/embed" -H "Content-Type: application/json" -d '{"texts": ["example text 1", "example text 2"]}'
    Note:
        The request body must be in the following format:
        {
            "texts": ["string1", "string2", ...]
        }
    """
    logger.info(f"[POST /embedding/embed] Called with texts: {request.texts}")
    try:
        embeddings = embedding_service.embed(request.texts)
        for text, emb in zip(request.texts, embeddings):
            milvus_service.insert_embedding(emb, text)
        logger.info(f"[POST /embedding/embed] Success: {len(embeddings)} embeddings generated")
        return {"embeddings": embeddings}
    except Exception as e:
        logger.error(f"[POST /embedding/embed] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/models')
def get_models():
    logger.info("[GET /embedding/models] Called")
    try:
        models = embedding_service.available_models()
        logger.info(f"[GET /embedding/models] Success: {models}")
        return {"models": models}
    except Exception as e:
        logger.error(f"[GET /embedding/models] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/health')
def health_check():
    logger.info("[GET /embedding/health] Called")
    try:
        status = {"status": "ok", "model": embedding_service.get_model_name()}
        logger.info(f"[GET /embedding/health] Success: {status}")
        return status
    except Exception as e:
        logger.error(f"[GET /embedding/health] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/search', response_model=SearchResponse)
def search_embeddings(request: SearchRequest):
    logger.info(f"[POST /embedding/search] Called with query: {request.query}, top_k: {request.top_k}")
    try:
        query_emb = embedding_service.embed([request.query])[0]
        results = milvus_service.search(query_emb, top_k=request.top_k)
        search_results = []
        for hit in results[0]:
            search_results.append(SearchResult(
                id=hit.id,
                score=hit.distance,
                metadata=hit.entity.get('metadata', '')
            ))
        logger.info(f"[POST /embedding/search] Success: {len(search_results)} results")
        return {"results": search_results}
    except Exception as e:
        logger.error(f"[POST /embedding/search] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/rag/retrieve', response_model=RagRetrieveResponse)
async def rag_retrieve(request: RagRetrieveRequest):
    logger.info(f"[POST /embedding/rag/retrieve] Called with query: {request.query}, top_k: {request.top_k}")
    try:
        context_chunks = await rag_service.retrieve_context(request.query, top_k=request.top_k)
        prompt = rag_service.assemble_prompt(request.query, context_chunks)
        search_results = [SearchResult(id=chunk['id'], score=chunk['score'], metadata=chunk['metadata']) for chunk in context_chunks]
        logger.info(f"[POST /embedding/rag/retrieve] Success: {len(search_results)} context chunks")
        return {"prompt": prompt, "context_chunks": search_results}
    except Exception as e:
        logger.error(f"[POST /embedding/rag/retrieve] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/rag/complete', response_model=RagCompleteResponse)
async def rag_complete(request: RagCompleteRequest):
    logger.info(f"[POST /embedding/rag/complete] Called with query: {request.query}, top_k: {request.top_k}, max_tokens: {request.max_tokens}, temperature: {request.temperature}")
    try:
        context_chunks = await rag_service.retrieve_context(request.query, top_k=request.top_k)
        prompt = rag_service.assemble_prompt(request.query, context_chunks)
        answer = llm_service.generate(prompt, max_tokens=request.max_tokens, temperature=request.temperature)
        search_results = [SearchResult(id=chunk['id'], score=chunk['score'], metadata=chunk['metadata']) for chunk in context_chunks]
        logger.info(f"[POST /embedding/rag/complete] Success: answer generated, {len(search_results)} context chunks")
        return {"prompt": prompt, "context_chunks": search_results, "answer": answer}
    except Exception as e:
        logger.error(f"[POST /embedding/rag/complete] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 