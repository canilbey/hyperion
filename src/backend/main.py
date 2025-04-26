from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import logging
from services.chat.service import ChatService
from services.chat.storage import ChatStorageService
from services.model.service import ModelService
from services.file.config import FileConfig
from services.search.service import SearchService
from services.health.service import HealthService
from services.core.config import CoreConfig
from services.core.init_service import InitService
from models import (
    ChatRequest, ChatResponse, 
    SearchRequest, FileUploadResponse,
    ModelCreateRequest, ModelCreateResponse
)

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

# Initialize configurations
core_config = CoreConfig()
file_config = FileConfig()

# Initialize services
init_service = InitService(core_config)
model_service = ModelService(core_config, init_service.database)
chat_storage_service = ChatStorageService(init_service.database)
chat_service = ChatService(core_config, model_service, chat_storage_service, init_service.redis_pool)
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

@app.on_event("startup")
async def startup():
    await init_service.initialize()
    logger.info("Service startup completed")

@app.on_event("shutdown")
async def shutdown():
    await init_service.cleanup()
    logger.info("Service shutdown completed")

@app.get("/health")
async def health_check():
    return await health_service.check_health()

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        return await file_service.handle_upload(file, core_config.upload_dir)
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    return await chat_service.process_chat_request(
        request,
        chat_name=request.chat_name
    )

@app.get("/chats")
async def list_chats():
    """List all chat sessions with metadata"""
    return await chat_service.storage_service.list_chats()

@app.get("/chats/{identifier}/messages")
async def get_chat_history(identifier: str):
    """Get messages for a chat (either by ID or name)"""
    try:
        # Try to parse as UUID first
        from uuid import UUID
        chat_id = UUID(identifier)
        return await chat_service.storage_service.get_chat_history(chat_id=chat_id)
    except ValueError:
        # If not UUID, treat as chat_name
        return await chat_service.storage_service.get_chat_history(chat_name=identifier)

@app.patch("/chats/{identifier}")
async def update_chat(identifier: str, update_data: dict):
    """Update chat metadata (name, tags, etc.)"""
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        return await chat_service.storage_service.update_chat(chat_id=chat_id, update_data=update_data)
    except ValueError:
        return await chat_service.storage_service.update_chat(chat_name=identifier, update_data=update_data)

@app.delete("/chats/{identifier}")
async def delete_chat(identifier: str):
    """Delete a chat session (by ID or name)"""
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        return await chat_service.storage_service.delete_chat(chat_id=chat_id)
    except ValueError:
        return await chat_service.storage_service.delete_chat(chat_name=identifier)

@app.post("/chat/{identifier}")
async def continue_chat(identifier: str, request: ChatRequest):
    """Continue existing chat or create new one with identifier as name"""
    try:
        from uuid import UUID
        chat_id = UUID(identifier)
        return await chat_service.process_chat_request(request, chat_id=chat_id)
    except ValueError:
        return await chat_service.process_chat_request(request, chat_name=identifier)

@app.post("/search")
async def vector_search(request: SearchRequest):
    return await search_service.vector_search(request.query, request.top_k)

@app.post("/model/create", response_model=ModelCreateResponse)
async def create_model(request: ModelCreateRequest):
    return await model_service.create_model(request)

@app.get("/models")
async def list_models():
    """List all registered models"""
    return await model_service.list_models()

@app.get("/model/{model_id}")
async def get_model(model_id: str):
    """Get details of a specific model"""
    return await model_service.get_model(model_id)

@app.patch("/model/{model_id}")
async def update_model(model_id: str, update_data: dict):
    """Partial update of model configuration"""
    return await model_service.update_model(model_id, update_data)

@app.delete("/model/{model_id}")
async def delete_model(model_id: str):
    """Delete a model configuration"""
    return await model_service.delete_model(model_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)