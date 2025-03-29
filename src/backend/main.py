from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
import os
import redis.asyncio as redis
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import uuid
import logging
from services.chat_service import ChatService
from config.models import ModelConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5431/db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    upload_dir: str = os.getenv("UPLOAD_DIR", "/uploads")
    default_model_config: ModelConfig = {}

settings = Settings()
app = FastAPI()
database = Database(settings.database_url)
redis_pool = redis.from_url(settings.redis_url)

# Create upload directory if not exists
os.makedirs(settings.upload_dir, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_items=1)
    custom_config: Optional[ModelConfig] = None
    stream: bool = False

class ChatResponse(BaseModel):
    message: ChatMessage
    model_used: str
    provider: str
    usage: Optional[dict] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size: int

# Endpoints
@app.on_event("startup")
async def startup():
    await database.connect()
    await redis_pool.ping()
    logger.info("Service startup completed")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await redis_pool.close()
    logger.info("Service shutdown completed")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "database": "connected" if database.is_connected else "disconnected",
        "redis": "connected" if await redis_pool.ping() else "disconnected"
    }

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, file_id)
        
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(contents)
        }
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    chat_service = ChatService(request.custom_config or settings.default_model_config)
    return await chat_service.process_chat_request(
        messages=[m.dict() for m in request.messages],
        stream=request.stream
    )

@app.post("/search")
async def vector_search(request: SearchRequest):
    return {
        "results": [
            {"id": str(uuid.uuid4()), "score": 0.95, "text": "Sample result 1"},
            {"id": str(uuid.uuid4()), "score": 0.92, "text": "Sample result 2"}
        ][:request.top_k]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)