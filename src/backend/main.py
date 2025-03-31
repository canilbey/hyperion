from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import logging
from services.chat.service import ChatService
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
chat_service = ChatService(core_config, model_service)
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
    return await chat_service.process_chat_request(request)

@app.post("/search")
async def vector_search(request: SearchRequest):
    return await search_service.vector_search(request.query, request.top_k)

@app.post("/model/create", response_model=ModelCreateResponse)
async def create_model(request: ModelCreateRequest):
    return await model_service.create_model(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)