# Backend API Documentation

## Base URL
`http://localhost:8000`

## Authentication
No authentication required for these endpoints

## Models Endpoint

### Create Model
```
POST /model/create
```
Create and store a new model configuration

**Request Body:**
```json
{
  "provider": "openrouter|ollama|lm_studio",
  "model": "provider-model-id",
  "model_name": "unique-display-name",
  "system_prompt": "optional system instructions", 
  "api_key": "provider-api-key",
  "knowledge_table_name": "optional-rag-context",
  "knowledge_table_id": "optional-rag-id"
}
```

**Response:**
```json
{
  "status": "model created",
  "model_name": "model-id",
  "model_id": "uuid-string"
}
```

**Errors:**
- 400: Invalid request format or duplicate model name
- 500: Model creation failed

## Chat Endpoints

### Process Chat Message
```
POST /chat
```
Process chat messages using specified model

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "message text"
    }
  ],
  "custom_config": {
    "model_id": "uuid-of-model"
  },
  "stream": false,
  "chat_name": "optional-chat-name"
}

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
  },
  "chat_id": "uuid-string"
}
```

**Errors:**
- 400: Invalid request format
- 404: Model not found
- 500: Chat processing failed

### Get Chat History
```
GET /chats/{identifier}/messages
```
Retrieve full conversation history for a chat. The identifier can be either:
- chat_id (UUID format)
- chat_name (string)

**Response:**
```json
[
  {
    "message_id": 1,
    "role": "user",
    "content": "Hello",
    "usage": null,
    "created_at": "2025-03-31T12:00:00Z"
  },
  {
    "message_id": 2,
    "role": "assistant",
    "content": "Hi there!",
    "usage": {
      "input_tokens": 10,
      "output_tokens": 5
    },
    "created_at": "2025-03-31T12:00:01Z"
  }
]
```

**Errors:**
- 404: Chat not found
- 400: Invalid identifier format

## Other Endpoints

### Health Check
```
GET /health
```
Check service status

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
Upload files to server

**Form Data:**
- `file`: File to upload

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "original-name.txt",
  "content_type": "text/plain",
  "size": 1024
}
```

### Vector Search (Placeholder)
```
POST /search
```
Semantic search endpoint

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

### Create Model
```bash
curl -X POST http://localhost:8000/model/create \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "openrouter",
    "model_name": "anthropic/claude-3-opus",
    "api_key": "your_api_key"
  }'
```

### Chat Request Examples

Using chat_id:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "custom_config": {
      "model_id": "your-model-uuid"
    }
  }'
```

Using chat_name:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "custom_config": {
      "model_id": "your-model-uuid"
    },
    "chat_name": "my-conversation"
  }'
```

Get chat history:
```bash
# By chat_id
curl http://localhost:8000/chats/123e4567-e89b-12d3-a456-426614174000/messages

# By chat_name
curl http://localhost:8000/chats/my-conversation/messages
```

## Rate Limits
- Default: 60 requests per minute per endpoint
- Adjustable via Redis configuration