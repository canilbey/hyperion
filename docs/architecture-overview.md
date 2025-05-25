# Architecture Overview

## Main Components
- Core Backend API & Auth
- Chat & Conversation Engine
- Document Ingestion & Processing
- Embedding & Vectorization
- Vector Database Integration (Milvus)
- RAG Retrieval & Context Assembly
- Frontend Application
- Workflow Orchestration & Automation
- Observability, Monitoring & DevOps

## Data Flow
1. Users interact with the Frontend Application.
2. User actions trigger API calls to the Core Backend API & Auth for authentication and user management.
3. Chat sessions and messages are managed by the Chat & Conversation Engine, which integrates with LLMs and Redis for context management.
4. Documents are uploaded and processed by the Document Ingestion & Processing module, which handles parsing, chunking, and metadata extraction.
5. Text chunks are sent to the Embedding & Vectorization module, where they are converted into vector representations.
6. Embeddings are stored in the Vector Database (Milvus), with metadata for model-based separation.
7. RAG Retrieval & Context Assembly handles query embedding, vector search, metadata filtering, and context assembly for LLMs.
8. Workflow Orchestration & Automation (e.g., Apache Airflow) automates document processing and embedding pipelines.
9. Observability, Monitoring & DevOps ensure system health, logging, metrics, and automated deployment.

## Integration Points
- API endpoints connect the frontend to backend services.
- Redis is used for caching and context window management.
- Milvus is used for vector storage and search.
- LLMs are integrated for chat and retrieval-augmented generation.
- Monitoring and logging are centralized via ELK, Prometheus, and Grafana.
- CI/CD and container orchestration are managed with Docker and Kubernetes. 