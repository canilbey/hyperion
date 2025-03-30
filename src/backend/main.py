from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from databases import Database
import os
import redis.asyncio as redis
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal
import uuid
import logging
from services.chat_service import ChatService
from services.model_service import ModelService
from config.models import ModelProvider

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
database = Database(os.getenv("DATABASE_URL", "postgresql://user:pass@db:5431/db"))
redis_pool = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
upload_dir = os.getenv("UPLOAD_DIR", "/uploads")

# Initialize services
model_service = ModelService(database)
chat_service = ChatService(model_service)

# Create upload directory if not exists
os.makedirs(upload_dir, exist_ok=True)

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

class ModelConfigRequest(BaseModel):
    model_id: Optional[str] = Field(
        default=None,
        description="Either model_id or model_name must be provided"
    )
    model_name: Optional[str] = Field(
        default=None,
        description="Either model_id or model_name must be provided"
    )
    provider: Optional[ModelProvider] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    knowledge_table: Optional[str] = None
    temperature: Optional[float] = None

    @field_validator('model_id', 'model_name', mode='before')
    def check_at_least_one_identifier(cls, v, info):
        if not v and not info.data.get('model_name' if info.field_name == 'model_id' else 'model_id'):
            raise ValueError("Either model_id or model_name must be provided")
        return v

class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_items=1)
    custom_config: Optional[ModelConfigRequest] = None
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

class ModelCreateRequest(BaseModel):
    provider: ModelProvider = ModelProvider.OPENROUTER
    model: str = "deepseek/deepseek-chat-v3-0324:free"
    model_name: str = "Deepseek Chat v3"
    system_prompt: str = "You are a helpful assistant."
    api_key: Optional[str] = None
    knowledge_table_name: Optional[str] = None
    knowledge_table_id: Optional[str] = None

class ModelCreateResponse(BaseModel):
    status: str
    model_name: str
    model_id: str

# Endpoints
@app.on_event("startup")
async def startup():
    await database.connect()
    await redis_pool.ping()
    
    # Create models table if not exists
    await database.execute("""
        CREATE TABLE IF NOT EXISTS models (
            model_id UUID PRIMARY KEY,
            provider VARCHAR(20) NOT NULL,
            model_name VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            system_prompt TEXT,
            api_key TEXT,
            knowledge_table_name VARCHAR(100),
            knowledge_table_id VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
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
        file_path = os.path.join(upload_dir, file_id)
        
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
    try:
        logger.info("Chat request received", extra={
            "event": "chat_request_received",
            "request": {
                "messages": [m.dict() for m in request.messages],
                "custom_config": request.custom_config.dict() if request.custom_config else None,
                "stream": request.stream
            }
        })

        if not request.custom_config:
            raise HTTPException(
                status_code=400,
                detail="Custom config with model_id or model_name is required"
            )

        model_config = await model_service.get_model_config(
            model_id=request.custom_config.model_id,
            model_name=request.custom_config.model_name
        )
        
        response = await chat_service.process_chat_request(
            messages=[m.dict() for m in request.messages],
            model_config=model_config,
            stream=request.stream
        )

        logger.info("Chat request completed", extra={
            "event": "chat_request_completed",
            "response": response
        })
        
        return response
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}", exc_info=True, extra={
            "event": "chat_request_failed",
            "error": str(e),
            "request": {
                "messages": [m.dict() for m in request.messages],
                "custom_config": request.custom_config.dict() if request.custom_config else None
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def vector_search(request: SearchRequest):
    return {
        "results": [
            {"id": str(uuid.uuid4()), "score": 0.95, "text": "Sample result 1"},
            {"id": str(uuid.uuid4()), "score": 0.92, "text": "Sample result 2"}
        ][:request.top_k]
    }

@app.post("/model/create", response_model=ModelCreateResponse)
async def create_model(request: ModelCreateRequest):
    return await model_service.create_model(
        provider=request.provider,
        model=request.model,
        model_name=request.model_name,
        system_prompt=request.system_prompt,
        api_key=request.api_key,
        knowledge_table_name=request.knowledge_table_name,
        knowledge_table_id=request.knowledge_table_id
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)