# Tech Context

## Temel Teknolojiler
- **Backend**: Python 3.10+, FastAPI
- **Database**: PostgreSQL (metadata), Redis (cache), Milvus (vectors)
- **AI/ML**: Sentence Transformers (all-MiniLM-L6-v2), PyTorch CPU
- **LLM Integration**: OpenRouter, OpenAI, Anthropic APIs
- **Frontend**: React, Redux (planned)
- **Containerization**: Docker, Docker Compose
- **File Processing**: PyPDF2 (PDF), built-in text parsing

## RAG Pipeline Stack
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Vector Database**: Milvus standalone with etcd, MinIO
- **Text Storage**: PostgreSQL text_chunks table
- **Search**: L2 distance metric, IVF_FLAT index
- **Context Assembly**: Async PostgreSQL queries + Milvus vector search

## Bağımlılıklar
- **Core**: FastAPI, uvicorn, databases, asyncpg
- **AI/ML**: sentence-transformers, torch (CPU-only), transformers
- **Vector DB**: pymilvus, milvus standalone
- **Database**: psycopg2-binary, redis
- **File Processing**: PyPDF2, python-multipart
- **HTTP**: httpx (async), requests
- **Authentication**: python-jose, passlib, bcrypt

## Performance Optimizations
- **Docker Build**: Multi-stage builds, CPU-only PyTorch (2.4GB vs 10GB+)
- **Build Time**: Optimized layer caching (7 min vs 30+ min)
- **Memory**: CPU-only embeddings, efficient tensor handling
- **Database**: Connection pooling, async operations
- **Caching**: Redis for model configs and chat history

## Development Environment
- **Local**: Docker Compose development stack
- **Testing**: pytest, docker-compose.test.yml
- **Database**: PostgreSQL migrations, automated schema management
- **Monitoring**: Comprehensive logging, health checks

## Teknik Kısıtlar
- **Embedding Model**: Fixed 384-dimension output (sentence-transformers)
- **File Types**: Currently PDF, TXT (DOCX planned)
- **Scalability**: Single-node Milvus (cluster mode available)
- **Memory**: Large document processing optimization needed
- **Dependencies**: CPU-only PyTorch for container size optimization
- **LLM APIs**: External provider dependency (OpenRouter/OpenAI)

## Production Considerations
- **Security**: API key management, input validation
- **Monitoring**: Logging, health checks, error tracking
- **Scaling**: Milvus clustering, Redis clustering, database sharding
- **Backup**: Vector data backup strategies, PostgreSQL backups
- **Updates**: Model version management, embedding consistency 