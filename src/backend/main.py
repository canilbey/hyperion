from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import logging
from backend.services.chat import ChatServiceManager, ChatConfig
from backend.services.model import ModelServiceManager, ModelConfig
from backend.services.file.config import FileConfig
from backend.services.search.service import SearchService
from backend.services.health.service import HealthService
from backend.services.core.config import CoreConfig
from backend.services.core.init_service import InitService
from backend.models import (
    ChatRequest, ChatResponse, 
    SearchRequest, FileUploadResponse,
    ModelCreateRequest, ModelCreateResponse,
    ChatMessage
)
from backend.services.auth import router as auth_router
from backend.routers import embedding as embedding_router
from backend.services.file.service import FileService
from backend.services.milvus_service import MilvusService
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enable debug logging for our services
for name in ['services', 'main']:
    logging.getLogger(name).setLevel(logging.DEBUG)

app = FastAPI()

# Configure file upload limits
app.state.max_file_size = 104857600  # 100MB

# Initialize configurations
core_config = CoreConfig()
file_config = FileConfig()
model_config = ModelConfig()
chat_config = ChatConfig()

# Initialise core *first* so that db / redis handles are ready
init_service = InitService(core_config)

# These managers depend on the handles that `init_service.initialize` prepares.
# Therefore, build them inside the `startup` lifecycle hook after core is up.
model_service_manager: ModelServiceManager  # type: ignore [var-annotated]
chat_service_manager: ChatServiceManager    # type: ignore
search_service = SearchService(core_config)
health_service = HealthService(core_config, init_service)

# Create upload directory if not exists
os.makedirs(core_config.upload_dir, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(embedding_router.router, prefix="/embedding")

@app.on_event("startup")
async def startup():
    global model_service_manager, chat_service_manager
    try:
        # Initialize core services
        await init_service.initialize()
        logger.info("Core services initialized")
        
        # Initialize model service manager
        model_service_manager = ModelServiceManager(init_service.database, model_config)
        await model_service_manager.initialize()
        logger.info("Model service initialized")
        
        # Initialize chat service manager
        chat_service_manager = ChatServiceManager(
            model_service=model_service_manager.service,
            database=init_service.database,
            redis=init_service.redis_pool
        )
        await chat_service_manager.initialize()
        logger.info("Chat service initialized")
        
        logger.info("Service startup completed successfully")
    except Exception as e:
        logger.error(f"Service startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    await init_service.cleanup()
    logger.info("Service shutdown completed")

@app.get("/health")
async def health_check():
    logger.info("[GET /health] Health check endpoint called")
    try:
        result = await health_service.check_health()
        logger.info(f"[GET /health] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[GET /health] Error: {e}")
        raise

@app.get("/api/health")
async def api_health_check():
    logger.info("[GET /api/health] Health check endpoint called")
    try:
        result = await health_service.check_health()
        logger.info(f"[GET /api/health] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[GET /api/health] Error: {e}")
        raise

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"[POST /upload] File upload requested: filename={file.filename}")
    try:
        from backend.services.file.service import FileService
        from backend.services.embedding_service import EmbeddingService
        from backend.services.milvus_service import MilvusService
        
        file_service = FileService(file_config)
        embedding_service = EmbeddingService()
        milvus_service = MilvusService()
        
        # Dosyayı kaydet ve parse et, metadata DB'ye yazılır
        result = await file_service.handle_file_upload(file, core_config.upload_dir, init_service.database)
        file_id = result.file_id
        file_path = os.path.join(core_config.upload_dir, file_id)
        text_chunks = file_service.parse_file(file_id, file_path, result.content_type)
        
        # Parse edilen chunk'ları veritabanına kaydet
        await file_service.save_text_chunks(init_service.database, text_chunks)
        logger.info(f"[POST /upload] Saved {len(text_chunks)} text chunks to database")
        
        # Embedding generation ve vector storage
        if text_chunks:
            logger.info(f"[POST /upload] Starting embedding generation for {len(text_chunks)} chunks")
            chunk_texts = [chunk.text for chunk in text_chunks]
            embeddings = embedding_service.embed(chunk_texts)
            for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
                metadata = f"file:{file_id}:chunk:{chunk.chunk_index}:filename:{result.filename}"
                milvus_service.insert_embedding(embedding, metadata)
            logger.info(f"[POST /upload] Generated and stored {len(embeddings)} embeddings in vector DB")
        logger.info(f"[POST /upload] File uploaded, parsed and embedded successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"[POST /upload] File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Purpose:
        Start a new chat session or send a message to the chat engine.
    Usage:
        POST /chat
        Body: JSON with chat request fields
    Role in the System:
        Entry point for chat-based interactions and conversation management.
    Authentication/Authorization:
        Requires authentication if chat is user-specific.
    Example Usage (cURL):
        curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"message": "Hello!"}'
    """
    return await chat_service_manager.service.process_chat_request(
        request,
        chat_name=request.chat_name
    )

@app.get("/chats")
async def list_chats():
    logger.info("[GET /chats] List chats endpoint called")
    try:
        result = await chat_service_manager.service.storage_service.list_chats()
        logger.info(f"[GET /chats] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[GET /chats] Error: {e}")
        raise

@app.get("/chats/{identifier}/messages", response_model=List[ChatMessage])
async def get_chat_history(identifier: str):
    logger.info(f"[GET /chats/{identifier}/messages] Get chat history called: identifier={identifier}")
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        result = await chat_service_manager.service.storage_service.get_chat_history(chat_id=chat_id)
        logger.info(f"[GET /chats/{identifier}/messages] Success: {result}")
        return result
    except ValueError:
        result = await chat_service_manager.service.storage_service.get_chat_history(chat_name=identifier)
        logger.info(f"[GET /chats/{identifier}/messages] Success (by name): {result}")
        return result
    except Exception as e:
        logger.error(f"[GET /chats/{identifier}/messages] Error: {e}")
        raise

@app.patch("/chats/{identifier}")
async def update_chat(identifier: str, update_data: dict):
    logger.info(f"[PATCH /chats/{identifier}] Update chat called: identifier={identifier}, update_data={update_data}")
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        result = await chat_service_manager.service.storage_service.update_chat(chat_id=chat_id, update_data=update_data)
        logger.info(f"[PATCH /chats/{identifier}] Success: {result}")
        return result
    except ValueError:
        result = await chat_service_manager.service.storage_service.update_chat(chat_name=identifier, update_data=update_data)
        logger.info(f"[PATCH /chats/{identifier}] Success (by name): {result}")
        return result
    except Exception as e:
        logger.error(f"[PATCH /chats/{identifier}] Error: {e}")
        raise

@app.delete("/chats/{identifier}")
async def delete_chat(identifier: str):
    logger.info(f"[DELETE /chats/{identifier}] Delete chat called: identifier={identifier}")
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        result = await chat_service_manager.service.storage_service.delete_chat(chat_id=chat_id)
        logger.info(f"[DELETE /chats/{identifier}] Success: {result}")
        return result
    except ValueError:
        result = await chat_service_manager.service.storage_service.delete_chat(chat_name=identifier)
        logger.info(f"[DELETE /chats/{identifier}] Success (by name): {result}")
        return result
    except Exception as e:
        logger.error(f"[DELETE /chats/{identifier}] Error: {e}")
        raise

@app.post("/chat/{identifier}")
async def continue_chat(identifier: str, request: ChatRequest):
    """
    Purpose:
        Continue an existing chat or create a new one with a specific identifier.
    Usage:
        POST /chat/{identifier}
        Body: JSON with chat request fields
    Role in the System:
        Enables ongoing conversations under a persistent identifier.
    Authentication/Authorization:
        Requires authentication.
    Example Usage (cURL):
        curl -X POST "http://localhost:8000/chat/1234" -H "Content-Type: application/json" -d '{"message": "Continue this chat."}'
    """
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        return await chat_service_manager.service.process_chat_request(request, chat_id=chat_id)
    except ValueError:
        return await chat_service_manager.service.process_chat_request(request, chat_name=identifier)

@app.post("/search")
async def vector_search(request: SearchRequest):
    logger.info(f"[POST /search] Vector search called: query={request.query}, top_k={request.top_k}")
    try:
        result = await search_service.vector_search(request.query, request.top_k)
        logger.info(f"[POST /search] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[POST /search] Error: {e}")
        raise

@app.post("/model/create", response_model=ModelCreateResponse)
async def create_model(request: ModelCreateRequest):
    logger.info(f"[POST /model/create] Create model called: request={request}")
    try:
        result = await model_service_manager.create_model(request)
        logger.info(f"[POST /model/create] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[POST /model/create] Error: {e}")
        raise

@app.get("/models")
async def list_models():
    logger.info("[GET /models] List models endpoint called")
    try:
        result = await model_service_manager.list_models()
        logger.info(f"[GET /models] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[GET /models] Error: {e}")
        raise

@app.get("/model/{model_id}")
async def get_model(model_id: str):
    logger.info(f"[GET /model/{model_id}] Get model called: model_id={model_id}")
    try:
        result = await model_service_manager.get_model(model_id)
        logger.info(f"[GET /model/{model_id}] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[GET /model/{model_id}] Error: {e}")
        raise

@app.patch("/model/{model_id}")
async def update_model(model_id: str, update_data: dict):
    logger.info(f"[PATCH /model/{model_id}] Update model called: model_id={model_id}, update_data={update_data}")
    try:
        result = await model_service_manager.update_model(model_id, update_data)
        logger.info(f"[PATCH /model/{model_id}] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[PATCH /model/{model_id}] Error: {e}")
        raise

@app.delete("/model/{model_id}")
async def delete_model(model_id: str):
    logger.info(f"[DELETE /model/{model_id}] Delete model called: model_id={model_id}")
    try:
        result = await model_service_manager.delete_model(model_id)
        logger.info(f"[DELETE /model/{model_id}] Success: {result}")
        return result
    except Exception as e:
        logger.error(f"[DELETE /model/{model_id}] Error: {e}")
        raise

@app.get("/files", response_model=list[FileUploadResponse])
async def list_files():
    """Tüm dosya metadata'larını files tablosundan döner."""
    try:
        query = "SELECT file_id, original_filename, content_type, original_size, num_chunks, chunked_total_size, upload_time, user_id FROM files ORDER BY upload_time DESC"
        rows = await init_service.database.fetch_all(query)
        files = [
            FileUploadResponse(
                file_id=str(row["file_id"]) if row["file_id"] is not None else None,
                filename=row["original_filename"],
                content_type=row["content_type"],
                size=row["original_size"],
                num_chunks=row["num_chunks"],
                chunked_total_size=row["chunked_total_size"],
                upload_time=row["upload_time"],
                user_id=str(row["user_id"]) if row["user_id"] is not None else None
            )
            for row in rows
        ]
        return files
    except Exception as e:
        logger.error(f"[GET /files] Error: {e}")
        raise HTTPException(status_code=500, detail="Dosya listesi alınamadı")

@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Bir dosyayı tüm ilişkili verilerle birlikte siler (metadata, chunk, vector db)."""
    try:
        # 1. Dosya metadata'sını ve orijinal adını al
        query = "SELECT original_filename FROM files WHERE file_id = :file_id"
        row = await init_service.database.fetch_one(query, {"file_id": file_id})
        if not row:
            raise HTTPException(status_code=404, detail="Dosya bulunamadı")
        filename = row["original_filename"]

        # 2. Chunk'ları sil
        await init_service.database.execute("DELETE FROM text_chunks WHERE file_id = :file_id", {"file_id": file_id})
        # 3. Metadata'yı sil
        await init_service.database.execute("DELETE FROM files WHERE file_id = :file_id", {"file_id": file_id})
        # 4. Upload klasöründen dosyayı sil
        file_path = os.path.join(core_config.upload_dir, file_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        # 5. Vector DB'den ilgili embedding'leri sil
        milvus_service = MilvusService()
        expr = f"metadata like 'file:{file_id}:%'"
        milvus_service._connect_and_init()
        collection = milvus_service._collection
        # Milvus'ta metadata'ya göre silme
        ids_to_delete = []
        results = collection.query(expr, output_fields=["id", "metadata"])
        for r in results:
            if r["metadata"].startswith(f"file:{file_id}:"):
                ids_to_delete.append(r["id"])
        if ids_to_delete:
            collection.delete(f"id in [{','.join(map(str, ids_to_delete))}]")
        return {"status": "deleted", "file_id": file_id, "filename": filename}
    except Exception as e:
        logger.error(f"[DELETE /files/{{file_id}}] Error: {e}")
        raise HTTPException(status_code=500, detail="Dosya silinemedi")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)