# RAG Retrieval & Context Assembly - Checklist

## Milestone 1: Query Embedding & Vector Search (High Priority)
- [ ] Implement query embedding logic  
  _Convert user queries into vector representations for search._
- [x] Implement vector search in Milvus  
  _Retrieve relevant vectors from Milvus based on query embedding._

## Milestone 2: Metadata Filtering & Context Assembly (Medium Priority)
- [ ] Implement metadata-based filtering  
  _Filter search results by metadata (e.g., model_name, document type)._ 
- [ ] Implement context assembly logic  
  _Assemble retrieved vectors and metadata into context for LLM input._

## Milestone 3: Advanced Retrieval & Quality (Medium/Low Priority)
- [ ] Implement re-ranking and semantic chunking (optional)  
  _Improve retrieval quality with re-ranking models and semantic chunking._
- [ ] Add logging and error handling  
  _Log all operations and handle errors consistently._
- [ ] Write unit and integration tests  
  _Ensure reliability and correctness with automated tests._
- [ ] Document API endpoints with OpenAPI/Swagger  
  _Provide interactive API documentation._

## General Dependencies
- [] Set up and configure Milvus instance  
  _Install and configure Milvus for vector search._
- [ ] Set up pre-trained embedding and re-ranking models (optional)  
  _Install and configure models for embedding and re-ranking._
- [x] Set up FastAPI core  
  _Initialize FastAPI application structure._
- [ ] Set up monitoring and logging infrastructure  
  _Prepare Prometheus, ELK, and related tools._

## Responsible Roles
- Backend Developer
- QA Engineer

## References
- See project.md and prd.md for more details.

## Added (2024-05)
- [x] Model migration files are split into single statements (one file per table and index)
- [x] Automatic migration support added (migrations run automatically on backend startup)
- [x] Faulty migrations fixed, now safe and idempotent 