# API Referansı

Tüm API uç noktaları, açıklamaları ve örnek kullanımlar için lütfen [docs/api-documentation.md](../docs/api-documentation.md) dosyasına başvurun.

---

# Teknik Bağlam (Tech Context)

- unstructured ile belge işleme ve parent-child chunking
- Multilingual embedding modeli ile vektör üretimi (Milvus)
- Hibrit arama: BM25 (örn. Elasticsearch) + vektör arama + cross-encoder reranking
- Parent-child retrieval ve gelişmiş loglama
- RAGAs ile otomatik değerlendirme ve sentetik test seti
- Analitik veri gölü, dashboard ve A/B test altyapısı
- Modül iskeleti: unstructured_adapter, parent_child_chunker, embedding pipeline, bm25_service, vector_service, fusion, rerank, hybrid_search, parent_child_retriever, ragas_adapter, logger, feedback, dashboard_api

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

# techContext - Teknik Context Window Yönetimi

## Teknik Durum
- Prompt büyümesi ve context window taşması kontrol altına alındı.
- Token limiti aşılırsa eski mesajlar baştan siliniyor (truncate).

## Teknik Yol Haritası
- Gerçek token hesaplama entegrasyonu (örn. tiktoken).
- Eski mesajların otomatik özetlenmesi.
- Kullanıcıya context window uyarısı.
- Gelişmiş context ve RAG yönetimi stratejileri.

# LangChain Text Splitters ile Semantic Chunking Entegrasyon Planı

## Amaç
PDF chunking işlemi artık sayfa bazlı değil, semantic chunking ile yapılacak. Bunun için LangChain Text Splitters kullanılacak.

## Entegrasyon Adımları
1. **Gereksinimler:**
   - `langchain` kütüphanesi requirements.txt'ye eklenecek.
2. **PDF'ten Metin Çıkarma:**
   - Mevcut PDF parsing fonksiyonu ile tüm metin çıkarılacak.
3. **LangChain ile Semantic Chunking:**
   - `RecursiveCharacterTextSplitter` veya ihtiyaca göre başka bir splitter kullanılacak.
   - Chunk boyutu ve overlap, LLM context window'una göre ayarlanacak.
   - Örnek:
     ```python
     from langchain.text_splitter import RecursiveCharacterTextSplitter
     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ".", "!", "?", " "])
     chunks = splitter.split_text(pdf_text)
     ```
4. **Chunk Metadata'sı:**
   - Her chunk'a index, orijinal sayfa, başlık, dosya adı gibi metadata eklenecek.
5. **Embedding ve Vektör DB:**
   - Her chunk embedding'e dönüştürülüp metadata ile birlikte vektör veritabanına kaydedilecek.
6. **Search Pipeline:**
   - Kullanıcı sorgusu embedding'e dönüştürülüp semantic chunk'lar arasında vektör benzerliği ile arama yapılacak.
7. **Test ve Validasyon:**
   - Farklı PDF'lerle semantic chunking ve arama kalitesi test edilecek.

## Pipeline Akışı
1. PDF Yükle → Metin Çıkar
2. LangChain ile Semantic Chunking
3. Chunk + Metadata → Embedding
4. Embedding + Metadata → Vektör DB'ye Kaydet
5. Kullanıcı Sorgusu → Embedding → Vektör DB'de Semantic Search
6. Sonuçları Kullanıcıya Göster

## Dikkat Edilecekler
- Chunk boyutu ve overlap, kullanılan LLM'e göre optimize edilmeli.
- Metadata kaybolmamalı, arama sonuçlarında chunk'ın kaynağı gösterilmeli.
- Gerekirse splitter özelleştirilmeli (başlık bazlı bölme vs.).

---

Bu plan Hyperion'un RAG ve arama kalitesini artırmak için teknik yol haritası olarak kullanılacaktır. 