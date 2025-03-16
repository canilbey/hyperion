# Data Flow Specifications

## Ingestion Pipeline
```mermaid
sequenceDiagram
    participant User
    participant API
    participant Parser
    participant Embedder
    participant Milvus

    User->>API: Upload PDF/TXT
    API->>Parser: Process document
    Parser->>Embedder: Send text chunks
    Embedder->>Milvus: Store vectors
    Milvus-->>API: Confirm indexing
    API-->>User: Return file ID
```

## Query Processing
```mermaid
sequenceDiagram
    participant User
    participant API
    participant QueryEngine
    participant Milvus
    participant LLM

    User->>API: Submit query
    API->>QueryEngine: Process request
    QueryEngine->>Milvus: Semantic search
    Milvus-->>QueryEngine: Return context
    QueryEngine->>LLM: Generate response
    LLM-->>API: Formatted answer
    API-->>User: Final response