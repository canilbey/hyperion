# System Patterns

## Mimari Yapı
- Modüler FastAPI backend
- React tabanlı frontend
- Milvus ile vektör veritabanı entegrasyonu
- Redis ile önbellekleme ve oturum yönetimi
- PostgreSQL ile metadata yönetimi
- Sentence Transformers ile embedding generation
- Multi-provider LLM integration (OpenRouter, OpenAI, Anthropic)

## Ana Bileşenler
- **Core Backend API & Auth** - FastAPI, JWT authentication
- **Chat & Conversation Engine** - Real-time messaging with RAG integration
- **Document Ingestion & Processing** - PDF/TXT file upload and parsing
- **Embedding & Vectorization** - Sentence-transformers, automatic embedding generation
- **Vector Database Integration** - Milvus storage with metadata retrieval
- **RAG Retrieval & Context Assembly** - Semantic search + PostgreSQL text retrieval
- **LLM Integration** - Multiple provider support with dynamic model switching
- **Database Layer** - PostgreSQL, Redis, Milvus coordination

## RAG Pipeline Architecture
```
📁 File Upload
    ↓
📄 File Parsing (PDF/TXT)
    ↓
✂️ Text Chunking
    ↓
🧠 Embedding Generation (Sentence Transformers)
    ↓
🗄️ Dual Storage:
    ├── 📊 Milvus (Vector + Metadata)
    └── 🐘 PostgreSQL (Text Content)
    ↓
💬 Chat Query
    ↓
🔍 Vector Search (Milvus)
    ↓
📚 Content Retrieval (PostgreSQL)
    ↓
🤖 LLM Enhancement (System Prompt)
    ↓
📤 Enhanced Response
```

## Entegrasyon Noktaları
- **API Gateway Pattern** - FastAPI router'lar ile endpoint organization
- **Service Layer Pattern** - Chat, File, Model, RAG service separation
- **Database Abstraction** - Multiple database coordination
- **Vector Search Integration** - Milvus semantic search + PostgreSQL content retrieval
- **Async Processing** - Non-blocking embedding generation ve database operations
- **Error Handling** - Graceful fallbacks ve comprehensive logging
- **Container Orchestration** - Docker Compose ile multi-service management

## Data Flow Patterns
- **Upload Flow**: File → Parse → Chunk → Embed → Store (Dual)
- **Chat Flow**: Query → Embed → Search → Retrieve → Enhance → Respond  
- **RAG Integration**: Automatic context injection into chat system
- **Model Management**: Dynamic LLM provider switching
- **Cache Strategy**: Redis ile performance optimization

## Security Patterns
- JWT-based authentication
- API key management for LLM providers
- User data isolation (planned)
- Input validation ve sanitization
- Secure file upload handling 