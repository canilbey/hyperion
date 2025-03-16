# Hyperion API Reference v2.1

## Authentication
```http
POST /auth/token
Content-Type: application/json

{
  "client_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_secret": "your_client_secret"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

## Endpoint Structure

### Users
**Create User**  
`POST /users`
```json
{
  "email": "user@example.com",
  "roles": ["developer"],
  "permissions": ["vectors:read"]
}
```

### DataNodes
**Ingest Document**  
`POST /data-nodes/{nodeId}/documents`
```json
{
  "file": "base64_encoded_content",
  "metadata": {
    "source": "arxiv",
    "content_type": "application/pdf"
  }
}
```

### Analytics
**Query Metrics**  
`GET /analytics/queries?start=2025-03-01&end=2025-03-15`
```json
{
  "total_queries": 1423,
  "avg_response_time": 1.23,
  "top_queries": ["LLM applications", "RAG architecture"]
}
```

## Error Response
```json
{
  "error": "invalid_token",
  "error_description": "Expired JWT Token",
  "error_uri": "/docs/errors#invalid_token"
}
```

## Webhook Events
```json
{
  "event_id": "evt_1OeK2dJw",
  "type": "document.processed",
  "data": {
    "document_id": "doc_123",
    "status": "indexed"
  },
  "created": "2025-03-16T09:00:00Z"
}
```

## Deprecation Policy
```http
GET /v1/vectors HTTP/1.1
X-API-Version: 1.0
X-Deprecation-Message: "v1 deprecated - migrate to v2 by 2026-01-01"