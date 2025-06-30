# System Patterns and Future Improvements

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

## Chunking Pattern: Paragraf Bazlı ve Overlap'lı
- Chunk'lar öncelikle paragraf bazlı oluşturulur.
- Eğer bir paragraf 500 tokendan uzunsa, cümle bazında bölünür.
- Bölünen chunk'lar arasında son 1-2 cümle overlap edilir (bağlam kopmaması için).
- Token hesaplama için tiktoken veya benzeri bir tokenizer kullanılır.
- Her chunk'a detaylı metadata eklenir (paragraf no, chunk index, dosya adı, sayfa no).

## Hybrid Search Pattern
- Chunk'lar hem BM25 (Elasticsearch) hem de vektör arama (Milvus) ile indekslenir.
- Kullanıcı sorgusu geldiğinde, her iki arama motorundan ilk N sonuç alınır.
- Sonuçlar skor bazında normalize edilip birleştirilir (fusion).
- İlk 10-20 sonuç cross-encoder ile rerank edilir.
- Sonuçlar chunk metni, skor, kaynak ve metadata ile frontend'e döner. 

## OCR Integration Planning

### Current Limitation
- PDF işleme sistemi şu anda sadece metin tabanlı PDF'leri işleyebiliyor
- Taranan (scanned) veya görüntü bazlı PDF'ler için metin çıkarımı yapılamıyor
- Bu durum özellikle eski dokümanlar veya resmi belgeler için bir kısıtlama oluşturuyor

### Proposed Solution: OCR Integration

#### 1. OCR Altyapı Seçenekleri
- **Tesseract OCR**
  - Açık kaynak
  - Yerel çalışabilme
  - Türkçe dahil çoklu dil desteği
  - Düşük maliyet
  
- **Cloud Vision API (Google/Azure)**
  - Yüksek doğruluk oranı
  - Hızlı işlem süresi
  - Ölçeklenebilirlik
  - API maliyeti

#### 2. Teknik Gereksinimler
- PDF sayfalarını görüntüye çevirme
- Görüntü/metin tespiti
- OCR işlem kuyruğu
- Sonuçların önbelleklenmesi
- Hata yönetimi ve yeniden deneme mekanizması

#### 3. İş Akışı
1. PDF yüklendiğinde sayfa tipini tespit et (görüntü/metin)
2. Görüntü bazlı sayfalar için:
   - Görüntü çıkarımı
   - OCR işlemi
   - Metin temizleme ve normalizasyon
   - Mevcut chunking pipeline'ına aktarım

#### 4. Performans Optimizasyonu
- Paralel işleme
- Önbellekleme stratejisi
- Batch processing
- Asenkron işlem kuyruğu

#### 5. Kalite Kontrol
- OCR doğruluk metriklerinin takibi
- Kullanıcı geri bildirimi mekanizması
- Sürekli iyileştirme döngüsü

### Implementation Phases

1. **Phase 1: Temel OCR Entegrasyonu**
   - Tesseract OCR entegrasyonu
   - Basit görüntü/metin tespiti
   - Temel hata yönetimi

2. **Phase 2: Gelişmiş Özellikler**
   - Cloud OCR servisleri entegrasyonu
   - Çoklu dil desteği optimizasyonu
   - Önbellekleme sistemi

3. **Phase 3: Ölçeklendirme**
   - Asenkron işlem kuyruğu
   - Paralel işleme
   - Performans optimizasyonları

4. **Phase 4: İyileştirme**
   - Kullanıcı geri bildirimi sistemi
   - Doğruluk oranı iyileştirmeleri
   - Monitoring ve analitik

### Success Metrics
- OCR doğruluk oranı
- İşlem süresi
- Sistem kaynak kullanımı
- Kullanıcı memnuniyeti
- Hata oranları 