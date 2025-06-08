# RAG Retrieval & Context Assembly - Project Overview

## Purpose
The RAG Retrieval & Context Assembly sub-project is responsible for retrieving relevant vector embeddings from the vector database (Milvus), applying metadata filtering, and assembling context for LLM-based response generation. It enables advanced retrieval-augmented generation workflows for the Hyperion platform.

## Scope
- Query embedding and vector search in Milvus
- Metadata-based filtering (e.g., model_name, document type)
- Context assembly for LLM input
- Advanced re-ranking and semantic chunking (mid/long term)
- Logging, error handling, and observability

## Architecture
- FastAPI service for retrieval and context assembly
- Integration with Milvus for vector search
- Metadata filtering and context assembly logic
- Optional re-ranking and semantic chunking modules
- Logging and monitoring integrated with Prometheus and ELK

## Technologies
- FastAPI (Python 3.10+)
- Milvus (vector database)
- Re-ranking models (optional, e.g., cross-encoders)
- Monitoring: Prometheus, ELK stack

## Dependencies
- Running Milvus instance for vector search
- Pre-trained embedding and re-ranking models (optional)
- Environment variables for DB/model connections, monitoring endpoints
- Logging and monitoring infrastructure

## Configuration Requirements
- Milvus connection and search configuration
- Metadata filtering rules
- Logging and monitoring endpoints

## Integration Points
- Receives queries from frontend or chat engine
- Retrieves vectors from Milvus and assembles context for LLM
- Exposes OpenAPI/Swagger documentation for integration
- System-wide logging and monitoring

## Workflow Description
- Receives a query and user context
- Embeds the query and searches Milvus for relevant vectors
- Applies metadata filtering and assembles context
- Optionally re-ranks and chunks results for LLM input
- All actions are logged and monitored

## References
- See prd.md for requirements and architecture
- Related sub-projects: Vector Database Integration, Chat & Conversation Engine, Observability & DevOps 