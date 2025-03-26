# Backend API Documentation

## Base URL
`http://localhost:8000`

## Authentication
No authentication required for these endpoints

## Endpoints

### Health Check
```
GET /health
```
Check service status and database connections

**Response:**
```json
{
  "status": "ok",
  "database": "connected|disconnected",
  "redis": "connected|disconnected"
}
```

### File Upload
```
POST /upload
```
Upload files to the server

**Form Data:**
- `file`: File to upload (required)

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "original-name.txt",
  "content_type": "text/plain",
  "size": 1024
}
```

**Errors:**
- 500: File upload failed

### Chat API
```
POST /chat
```
Process chat messages with optional RAG context

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "message text"
    }
  ],
  "model_config": {
    "provider": "OPENROUTER|OLLAMA|LM_STUDIO",
    "model": "model-name",
    "temperature": 0.7,
    "knowledge_table": "optional-rag-context"
  },
  "stream": false
}
```

**Response:**
```json
{
  "message": {
    "role": "assistant",
    "content": "response text"
  },
  "model_used": "model-name",
  "provider": "provider-name",
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

**Errors:**
- 400: Invalid request format
- 500: Chat processing failed

### Vector Search
```
POST /search
```
Semantic search (Milvus placeholder)

**Request Body:**
```json
{
  "query": "search terms",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid-string",
      "score": 0.95,
      "text": "result text"
    }
  ]
}
```

## Usage Examples

### Using cURL

1. Start services:
```bash
docker-compose up -d --build backend
```

2. Test health check:
```bash
curl http://localhost:8000/health
```

3. Upload a file:
```bash
curl -X POST http://localhost:8000/upload -F "file=@README.md"
```

4. Chat example:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

### Using Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# File upload
with open("test.txt", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/upload", files=files)
    print(response.json())

# Chat request
chat_data = {
    "messages": [{"role": "user", "content": "Hello"}],
    "model_config": {
        "provider": "OPENROUTER",
        "model": "gpt-3.5-turbo"
    }
}
response = requests.post("http://localhost:8000/chat", json=chat_data)
print(response.json())
```

## Rate Limits
- Default: 60 requests per minute per endpoint
- Adjustable via Redis configuration