# Document Ingestion & Processing - Project Overview

## Purpose
The Document Ingestion & Processing sub-project is responsible for handling the upload, parsing, chunking, and metadata extraction of documents (PDF/text) for the Hyperion platform. It ensures reliable document management and prepares data for downstream embedding and retrieval workflows.

## Scope
- Upload and manage PDF/text files
- Parse documents and extract text content
- Chunk documents for efficient processing
- OCR support for scanned documents and images
- Multi-column and complex layout handling
- Metadata extraction and management
- Logging, error handling, and observability

## Architecture
- Modular FastAPI service structure
- Persistent storage for uploaded files and metadata (e.g., PostgreSQL, S3, or local storage)
- OCR integration (e.g., Tesseract) for scanned documents
- Document parsing and chunking pipeline
- Logging and monitoring integrated with Prometheus and ELK

## Technologies
- FastAPI (Python 3.10+)
- PostgreSQL or S3/local storage (file/metadata storage)
- Tesseract OCR (for scanned documents)
- PDF/text parsing libraries (PyPDF2, pdfplumber, etc.)
- Monitoring: Prometheus, ELK stack

## Dependencies
- Running PostgreSQL or S3/local storage for files and metadata
- OCR library (Tesseract) installed and configured
- Environment variables for storage, OCR, and monitoring endpoints
- Logging and monitoring infrastructure

## Configuration Requirements
- Database schema for file and metadata storage
- OCR configuration and language packs
- Logging and monitoring endpoints

## Integration Points
- Provides parsed and chunked documents to Embedding & Vectorization module
- Exposes OpenAPI/Swagger documentation for frontend and external integration
- Integrates with user/auth service for access control
- System-wide logging and monitoring

## Workflow Description
- User uploads a document via the API
- System parses and extracts text, applies OCR if needed
- Document is chunked and metadata is extracted
- Processed data is stored and made available for embedding
- All actions are logged and monitored

## References
- See prd.md for requirements and architecture
- Related sub-projects: Embedding & Vectorization, Core Backend API & Auth, Observability & DevOps

## Yenilikler ve İyileştirmeler (2025-06)
- **Çok Dilli Embedding Modeli:** Varsayılan model `paraphrase-multilingual-MiniLM-L12-v2` olarak güncellendi. Türkçe ve diğer dillerde yüksek doğruluk.
- **Preprocessing Pipeline:** Tüm metinler (doküman chunk'ları ve sorgular) için unicode normalization, lower, strip ve fazla boşluk temizliği uygulanır.
- **Chunking:** LangChain RecursiveCharacterTextSplitter ile 500 karakter, 50 overlap, Türkçe için optimize ayraçlar.
- **Tutarlı Embedding:** Hem doküman yüklemede hem aramada aynı preprocessing uygulanır.
- **Test:** Türkçe doküman ve sorgularla başarıyla test edilmiştir.

## OCR Integration Project

### Overview
Taranan (scanned) PDF belgelerinden metin çıkarımı için OCR entegrasyonu planlaması.

### Problem Statement
Mevcut sistem sadece metin tabanlı PDF'leri işleyebiliyor. Taranan belgeler, fotoğraflar veya görüntü bazlı PDF'lerden metin çıkarımı yapılamıyor. Bu durum, özellikle eski dokümanlar ve resmi belgeler için önemli bir kısıtlama oluşturuyor.

### Goals
1. Görüntü bazlı PDF'lerden metin çıkarımı
2. Yüksek doğruluk oranı (>%90)
3. Kabul edilebilir işlem süresi
4. Türkçe karakter desteği
5. Ölçeklenebilir çözüm

### Technical Solution

#### OCR Engine Options
1. **Tesseract OCR (Phase 1)**
   - Açık kaynak
   - Self-hosted çözüm
   - Türkçe desteği
   - Düşük maliyet
   - Orta seviye doğruluk

2. **Cloud Vision API (Phase 2)**
   - Google Cloud Vision veya Azure Computer Vision
   - Yüksek doğruluk
   - API bazlı maliyet
   - Kolay entegrasyon
   - Hızlı işlem süresi

#### Implementation Details

1. **PDF İşleme Pipeline Güncellemesi**
```python
def process_pdf(file_path):
    # 1. Sayfa tipi tespiti
    page_types = detect_page_types(file_path)
    
    # 2. Sayfa işleme
    for page, type in page_types:
        if type == 'image':
            # OCR işlemi
            text = perform_ocr(page)
        else:
            # Normal metin çıkarımı
            text = extract_text(page)
            
        # 3. Metin temizleme
        cleaned_text = clean_and_normalize(text)
        
        # 4. Chunking
        chunks = create_chunks(cleaned_text)
```

2. **OCR İşlem Kuyruğu**
```python
class OCRQueue:
    def __init__(self):
        self.queue = Queue()
        self.results = {}
        
    async def process_batch(self):
        while True:
            batch = self.queue.get_batch()
            results = await parallel_ocr(batch)
            self.results.update(results)
```

3. **Önbellekleme**
```python
class OCRCache:
    def __init__(self):
        self.cache = {}
        
    def get(self, image_hash):
        return self.cache.get(image_hash)
        
    def set(self, image_hash, text):
        self.cache[image_hash] = text
```

### Infrastructure Requirements

1. **Storage**
   - OCR sonuçları için cache storage
   - Görüntü işleme için geçici storage
   - Backup sistemi

2. **Computing**
   - OCR işlemleri için CPU/GPU
   - Paralel işlem kapasitesi
   - Auto-scaling desteği

3. **Network**
   - Cloud OCR servisleri için bant genişliği
   - Load balancing
   - Fault tolerance

### Monitoring & Analytics

1. **Performance Metrics**
   - OCR doğruluk oranı
   - İşlem süresi
   - Kaynak kullanımı
   - Hata oranları

2. **User Feedback**
   - Doğruluk geri bildirimi
   - Manuel düzeltme sistemi
   - Kullanıcı memnuniyeti takibi

### Timeline & Phases

1. **Phase 1 (2-3 ay)**
   - Tesseract OCR entegrasyonu
   - Temel görüntü işleme
   - Pipeline güncellemesi

2. **Phase 2 (2-3 ay)**
   - Cloud OCR entegrasyonu
   - Önbellekleme sistemi
   - Performans optimizasyonu

3. **Phase 3 (2-3 ay)**
   - Ölçeklendirme
   - Monitoring sistemi
   - Kullanıcı geri bildirimi

### Success Criteria

1. **Technical**
   - >90% OCR doğruluk oranı
   - <30 sn sayfa başına işlem süresi
   - <1% hata oranı

2. **Business**
   - Kullanıcı memnuniyeti artışı
   - Sistem kullanım artışı
   - Support ticket azalması

### Risks & Mitigations

1. **Technical Risks**
   - OCR doğruluk sorunları
   - Performans darboğazları
   - Ölçeklendirme zorlukları

2. **Mitigations**
   - Çoklu OCR engine kullanımı
   - Asenkron işlem kuyruğu
   - Auto-scaling ve load balancing 