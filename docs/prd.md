# Product Requirements Document (PRD)

## 1. Project Vision & Goals
Hyperion is an open-source, modular, and scalable Retrieval-Augmented Generation (RAG) platform designed to enable advanced document-based conversational AI. The system empowers users to upload documents, create model-specific knowledge bases, and interact with LLMs that leverage external context for accurate, up-to-date responses.

**Primary Goals:**
- Seamless integration of document ingestion, vectorization, and retrieval for LLMs
- Support for multiple models and model-specific knowledge pools
- High performance, extensibility, and open-source best practices

## 2. User Types & Key Scenarios
- **End Users:** Upload documents, select models, chat with LLMs, retrieve context-rich answers
- **Admins:** Manage models, monitor system health, configure pipelines, review logs
- **Developers:** Extend system with new models, chunkers, embedding pipelines, or integrations

## 3. System Architecture Overview
- **Frontend:** React-based web app for chat, document/model management, and analytics
- **Backend:** FastAPI-based modular API, with sub-services for chat, document processing, embedding, retrieval, and admin
- **Vector DB:** Milvus for high-performance vector storage and search
- **Workflow Orchestration:** Apache Airflow for document/embedding pipeline automation
- **Cache:** Redis for fast access to chat history, configs, and search results
- **Relational DB:** PostgreSQL for user, model, and document metadata
- **Monitoring:** Prometheus, Grafana, ELK for observability

## 4. Main Workflows
### 4.1 Document Ingestion & Processing
- Users upload PDF/text files
- Files are parsed, chunked (with advanced splitters, OCR if needed)
- Each chunk is embedded (Sentence Transformers, model-specific if needed)
- Embeddings and metadata (including model_name) are stored in Milvus

### 4.2 Chat & Retrieval
- User starts/selects a chat session and model
- User sends a message; backend retrieves full chat history
- Query is embedded and used to search Milvus (filtered by model_name)
- Top-k relevant chunks are retrieved and provided as context to the LLM
- LLM generates a response, which is stored and returned to the user

### 4.3 Model & Knowledge Base Management
- Admins can add new models, configure embedding pipelines, and manage model-specific knowledge pools
- Model versioning and metadata management

### 4.4 Workflow Automation
- Airflow automates document ingestion, embedding, and indexing
- Monitoring, error handling, and reprocessing are managed via Airflow DAGs

## 5. Sub-Project Structure & Integration
- **Core Backend API & Auth:** User management, JWT, RBAC, logging, error handling
- **Chat & Conversation Engine:** Chat session management, LLM context assembly, cache
- **Document Ingestion & Processing:** File upload, parsing, chunking, OCR
- **Embedding & Vectorization:** Embedding model selection, batch processing
- **Vector Database Integration (Milvus):** Collection/schema management, search, metadata filtering
- **RAG Retrieval & Context Assembly:** Query embedding, Milvus search, context window management
- **Frontend Application:** UI/UX, API integration, accessibility
- **Workflow Orchestration:** Airflow DAGs, monitoring, automation
- **Observability & DevOps:** Logging, metrics, CI/CD, deployment

## 6. Technical Requirements
- Python 3.10+, FastAPI, React, Milvus, Redis, PostgreSQL, Airflow
- Support for multi-lingual embedding models (e.g., all-mpnet-base-v2, TURNA)
- Scalable, containerized deployment (Docker, Kubernetes)
- API-based and direct Python module integration options
- Configurable chunking, embedding, and retrieval parameters
- Secure authentication, RBAC, and data encryption

## 7. Success Criteria & Metrics
- End-to-end chat latency < 2s (P95)
- Document ingestion to retrieval pipeline < 5 min for 100MB PDF
- >90% test coverage for backend and critical frontend flows
- 99.9% uptime for core services
- User feedback: >80% satisfaction on context relevance

## 8. Risks & Assumptions
- Large document processing and embedding may require GPU and parallelization
- Milvus performance tuning (indexing, nprobe, etc.) is critical for scale
- OCR and complex PDF layouts may introduce parsing errors
- Open-source dependencies must be actively maintained
- Assumes users have basic technical skills for setup and operation

## 9. Future Directions
- Multi-modal (image, audio) support
- Advanced re-ranking and semantic chunking
- User feedback loop for continuous improvement
- Distributed Milvus and scalable orchestration

---

*This PRD is the single source of truth for all sub-project and documentation efforts. All technical and planning documents will reference this PRD for requirements, architecture, and integration details.* 