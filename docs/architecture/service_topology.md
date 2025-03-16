# Service Topology Overview

## Core Components
```mermaid
flowchart TD
    subgraph Data Layer
        A[Milvus Vector DB] --> B[Redis Cache]
        C[PostgreSQL Metadata] --> A
    end
    
    subgraph Processing
        D[PDF Parser] --> E[Chunker]
        E --> F[Embedding Model]
        F --> A
    end
    
    subgraph Services
        G[API Server] -->|gRPC| H[Query Engine]
        H --> I[Prompt Engine]
        I --> J[LLM Gateway]
    end
```

## Interaction Matrix
| Service          | Protocol | Port  | Dependency          |
|------------------|----------|-------|---------------------|
| API Server       | HTTP/2   | 8000  | Query Engine        |
| Query Engine     | gRPC     | 50051 | Milvus, Redis       |
| LLM Gateway      | HTTP/1.1 | 8080  | External LLM APIs   |
| Milvus           | gRPC     | 19530 | -                   |