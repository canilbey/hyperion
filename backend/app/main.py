import time
import uuid
import os
import logging
import traceback

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import fitz  # PyMuPDF

# Import only what is needed from opentelemetry modules

# Import additional dependency used in query_rag
import httpx

# Create FastAPI app
app = FastAPI()


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
        start_time = time.time()
                
        try:
            file_id = str(uuid.uuid4())
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
            
            # Write uploaded file to disk
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Process file based on extension
            if file.filename.lower().endswith('.pdf'):
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
            else:
                with open(file_path, "r") as f:
                    text = f.read()
            
            return {"status": "success", "file_id": file_id}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Hyperion API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/api/query")
async def query_rag(request: Request):
        try:
            data = await request.json()
            query = data.get("query")
            
            # TODO: Implement FAISS/Milvus integration for vector retrieval
            context = "Sample context from vector store"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{os.getenv('OPENROUTER_BASE_URL')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": os.getenv("OPENROUTER_MODEL"),
                        "messages": [
                            {
                                "role": "system",
                                "content": f"Answer using this context: {context}"
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ]
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                return {
                    "answer": result['choices'][0]['message']['content'],
                    "metadata": result['usage']
                }
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error")
