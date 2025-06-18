# Hyperion Progress

## 🆕 Son Gelişmeler

- **✅ Unstructured Kütüphanesi Optimizasyonu:** Context7 MCP kullanarak en verimli unstructured kullanımını araştırdık ve uyguladık:
  - `partition.auto` ile otomatik format tespiti
  - Dosya boyutuna göre optimal strategy seçimi (fast/hi_res)
  - PDF için özel optimizasyonlar (tablo/görsel çıkarımı devre dışı)
  - Chunking parametreleri optimize edildi (by_title, max_characters=4000)
  - Çoklu fallback sistemi (unstructured → PyPDF2 → text → manual)
- **✅ libGL.so.1 hatası çözümü:** OpenCV bağımlılığından tamamen kaçınıldı.
- **✅ Docker container optimizasyonu:** Minimal sistem kütüphaneleri + poppler-utils eklendi.
- **✅ PDF parsing iyileştirmesi:** En doğru yöntem olarak unstructured partition.auto kullanılıyor.
- **✅ Attu (Milvus Web UI) docker-compose ile projeye eklendi ve Milvus bağlantısı başarıyla sağlandı.** Artık vektör veritabanı görsel olarak yönetilebiliyor, koleksiyonlar ve vektörler Attu arayüzünden incelenip silinebiliyor.
- **✅ Milvus bağlantı sorunları çözüldü:** Attu konteyneri için `MILVUS_URL=host.docker.internal:19530` ayarı ile bağlantı sağlandı.
- **✅ Chat listesinde silme butonu ve anında chat başlatma:** Chat listesinde her sohbet için silme butonu eklendi, yeni bir konuşma başladığında chat ekranı anında açılıyor.
- **✅ LLM yanıtlarında markdown render:** LLM'den gelen yanıtlar ve kullanıcı mesajları artık markdown olarak düzgün şekilde render ediliyor (react-markdown + remark-gfm ile).
- **✅ Dosya yükleme limiti artırıldı:** Backend'de dosya yükleme limiti 10MB → 1GB'a çıkarıldı. Frontend'de kullanıcıya maksimum dosya boyutu bilgisi gösteriliyor.
- **✅ OpenRouter API timeout artırıldı:** Büyük belge ve RAG context ile yapılan sorgularda timeout hatası yaşanmaması için OpenRouter, OpenAI ve Anthropic API çağrılarında timeout 60 saniyeye çıkarıldı.
- **✅ SQL ambiguous column hatası çözüldü:** Chat silme işlemlerinde yaşanan SQL hata ve UUID handling bug'ları giderildi.
- **✅ Frontend FileManager ve ChatContainer UI/UX iyileştirmeleri:** Dosya yönetimi ve chat arayüzü modernleştirildi, silme ve detay gösterimi optimize edildi.

## ✅ Tamamlanan Özellikler

### Backend Infrastructure
- **✅ FastAPI backend** - Tam çalışır durumda
- **✅ Database migrations** - Tüm servisler için migration'lar çalışıyor
- **✅ Service architecture** - Auth, Chat, Model, File servisleri
- **✅ Health check endpoints** - Monitoring ve status kontrolü
- **✅ Docker containerization** - Multi-service orchestration

### Build & Performance Optimizations
- **✅ PyTorch CPU optimization** - 10GB+ → 2.4GB container boyutu
- **✅ Build time optimization** - 30+ dakika → 7 dakika build süresi
- **✅ Multi-stage Dockerfile** - Optimized layer caching
- **✅ Timeout issues resolved** - CPU-only torch dependencies

### Authentication System
- **✅ User registration/login** - JWT token based
- **✅ Role-based access** - Admin/User role management
- **✅ Database integration** - PostgreSQL ile tam entegrasyon

### Chat System
- **✅ Chat management** - Chat oluşturma/listeleme
- **✅ Message handling** - User/Assistant message flow
- **✅ Context management** - Chat context tracking
- **✅ RAG Integration** - Chat'e otomatik RAG context ekleme
- **🟧 Eksikler:** Chat arayüzü istenen gibi değil ve backend entegrasyonu tam anlamıyla doğru çalışmıyor. Chat silme, chat ismi düzenleme ve chat geçmişi (history) UI'da düzgün çalışmıyor/görünmüyor. Frontend ve backend entegrasyonunda eksikler ve hatalar mevcut. Kullanıcı deneyimi ve işlevsellik açısından chat yönetimi yeniden ele alınmalı.

### File Processing System  
- **✅ File upload** - PDF/TXT dosya yükleme
- **✅ Text chunking** - Belge parsing ve chunk'lara bölme
- **✅ Database storage** - text_chunks tablosunda saklama
- **✅ Migration'lar çözüldü** - File servisi migration'ları aktif
- **✅ File Management Backend-Frontend Entegrasyonu** - Dosya yükleme, listeleme ve silme işlemleri backend ve frontend arasında uçtan uca entegre edildi. Migration, model ve servis güncellemeleri tamamlandı.

### RAG Pipeline (TAMAMEN TAMAMLANDI) 🎉
- **✅ Embedding generation** - Sentence transformers entegrasyonu tamamlandı
- **✅ Vector storage** - Milvus ile embedding saklama çalışıyor
- **✅ Vector search** - Query embedding'ler ile similarity search
- **✅ Context retrieval** - PostgreSQL'den text içerik çekme
- **✅ Chat integration** - RAG context otomatik chat'e ekleme
- **✅ LLM enhancement** - Belge bilgileri sistem prompt'u olarak ekleme
- **✅ End-to-end pipeline** - Upload → Parse → Embed → Store → Search → Chat

### Database Layer
- **✅ PostgreSQL** - Ana database
- **✅ Redis** - Cache layer
- **✅ Milvus** - Vector database (output_fields ile metadata retrieval)
- **✅ Migration system** - Automated schema management

### Model Integration
- **✅ Model creation** - Multiple LLM provider support
- **✅ OpenRouter API** - DeepSeek, Anthropic, OpenAI desteği
- **✅ Model configuration** - Database'de model config saklama
- **✅ Dynamic model switching** - Chat'te model_id ile seçim

## 🚧 Devam Eden Çalışmalar

### Frontend Development
- **✅ React frontend** - UI/UX geliştirme
- **✅ API integration & state management** - MVP düzeyinde tamamlandı
- **✅ File upload UI** - Drag & drop interface
- **✅ Chat interface** - Real-time messaging
- **Yeni:**
    - Sidebar: Model yönetimi, dosya yönetimi, yeni chat, chat listesi
    - Ana içerik: Tab'lı yapı (Chat, Model Yönetimi, Dosya Yönetimi)
    - Chat tabında sadece model seçimi ve chat alanı
    - Modern, minimal, responsive component breakdown
- **🟧 Son Durum:**
    - Chat silme ve geçmiş gösterimi UI'da düzgün çalışıyor, yalnızca başlık düzenleme eksik.
    - Diğer frontend alanları tamamlandı.
    - Karşılaşılan tipik sorunlar: build hataları (örn. package.json, build script, dist/build farkı), port çakışmaları, API endpoint uyumsuzlukları, bağlantı ve erişim hataları.
    - Çözüm önerileri ve yapılan düzeltmeler memory-bank'te güncelleniyor.
- **🟧 Yeni Gözlemlenen Problemler ve Öncelikli Geliştirme Adımları:**
    1. **Chat input box ekranın altında kayboluyor:** Chat ekranında input bar her zaman ekranın altına snap'li olmalı ve asla kaybolmamalı. Flex veya fixed layout ile sabitlenecek.
    2. **Modeller backend'den alınamıyor, dummy modeller görünüyor:** Model listesi sadece API'den gelen verilerle güncellenecek, hardcoded modeller kaldırılacak.
    3. **Model eklemede browser prompt yerine uygulama içi form/modal:** Model ekle butonuna basınca ana ekranda model konfigürasyon formu açılacak, kaydet ile backend'e gönderilecek.
    4. **Dosya yönetiminde drag & drop ile dosya ekleme:** FileManager'a drag & drop alanı eklenecek, dosya sürükleyip bırakınca backend'e yüklenecek.
    5. **Chats ekranında model seçimi:** Chat ekranında model seçimi için dropdown veya benzeri bir alan olacak, seçilen model ile mesaj gönderilecek.
    6. **API endpoint uyumsuzlukları ve eksik dosya listeleme:**
        - Model ekleme için frontend'de /model/create endpointi kullanılacak.
        - Dosya yükleme için frontend'de /upload endpointi kullanılacak.
        - Backend'e GET /files endpointi eklenecek (dosya listeleme için).

#### 🟦 Frontend-Backend Entegrasyon Planı (E2E)
- **Chat:**
    - Kullanıcı mesajı gönderdiğinde, `/chat` endpoint'ine POST isteği atılacak.
    - Dönen cevap arayüzde gösterilecek.
    - Chat geçmişi için gerekirse ek endpoint planlanacak.
- **Model Yönetimi:**
    - `GET /models` ile modeller listelenecek.
    - `POST /models` ile yeni model eklenecek.
    - `DELETE /models/{id}` ve `PUT /models/{id}` endpointleri eksikse backend'e eklenecek.
    - ModelManager ve ModelTab component'leri API ile entegre edilecek.
- **Dosya Yönetimi:**
    - `GET /files`, `POST /files/upload`, `DELETE /files/{id}`, `PUT /files/{id}` endpointleri ile dosya işlemleri yapılacak (eksikse backend'e eklenecek).
    - FileManager ve FileTab component'leri API ile entegre edilecek.
- **Sağlık Kontrolü:**
    - Uygulama başlatılırken `/health` endpoint'i ile backend durumu kontrol edilecek.
- **API Servis Katmanı:**
    - `/src/frontend/services/` altında chatService.js, modelService.js, fileService.js dosyaları oluşturulacak.
    - Her servis dosyasında ilgili endpointlere fetch/axios ile istek atan fonksiyonlar yazılacak.
- **State ve Hata Yönetimi:**
    - API çağrılarında loading ve error state'leri yönetilecek.
    - Kullanıcıya uygun geri bildirimler gösterilecek.
- **Ortam Değişkenleri:**
    - API URL'leri `.env` dosyası ile yönetilecek (örn: REACT_APP_API_URL).
- **Dockerize Etme:**
    - Frontend için Dockerfile yazılacak ve docker-compose ile backend ile birlikte ayağa kaldırılacak.
- **Test:**
    - Tüm ana akışlar (chat, model, dosya) uçtan uca test edilecek.

### Performance Optimizations
- **📋 Embedding caching** - Redis ile embedding cache
- **📋 Vector index optimization** - Milvus index tuning
- **📋 Chunk size optimization** - Optimal chunk boyutu belirleme

## 🎯 Sonraki Hedefler

1. **Frontend Development**  
   - Modern React UI
   - Responsive design
   - Real-time features
   - Document management interface
   - **Yeni:** Tab'lı ve sidebar'lı ana layout, component breakdown

2. **Advanced RAG Features**
   - Multi-document querying
   - Document filtering by metadata
   - Relevance scoring improvements
   - Context window optimization

3. **Production Readiness**
   - Environment configurations
   - Security hardening  
   - Performance monitoring
   - API rate limiting

## 📊 Teknik Başarılar

- **Build Optimization**: %75+ boyut azalma, %75+ hız artışı
- **Migration System**: Sıfırdan kurulumda hata yok
- **Service Architecture**: Modüler ve ölçeklenebilir yapı
- **Container Strategy**: CPU-optimized PyTorch deployment
- **RAG Pipeline**: Tamamen çalışır end-to-end RAG sistemi

## 🔧 Son Yapılan İyileştirmeler

- **✅ Chat listesinde silme butonu ve anında chat başlatma**
- **✅ LLM yanıtlarında markdown render**
- **✅ Dosya yükleme limiti artırıldı (1GB)**
- **✅ OpenRouter API timeout artırıldı (60s)**
- **✅ SQL ambiguous column ve UUID bug fix**
- **✅ Frontend FileManager ve ChatContainer UI/UX iyileştirmeleri**
- **✅ RAG Chat Integration** - Chat service'e RAG context otomatik ekleme
- **✅ Vector Search Fix** - Milvus output_fields ile metadata retrieval
- **✅ Async RAG Service** - Database integration ile text content çekme
- **✅ Error Handling** - HTTPException import ve graceful fallbacks
- **✅ Debug Logging** - RAG pipeline debugging ve monitoring

## 🚀 RAG Pipeline Detayları

### Tam Çalışan Pipeline:
```
📝 User Query → 🧠 Query Embedding → 🔍 Milvus Search → 📚 PostgreSQL Text Retrieval → 💬 Context Assembly → 🤖 LLM Call → 🔍 Enhanced Response
```

### Test Edilmiş Özellikler:
- ✅ File upload with embedding generation
- ✅ Vector storage in Milvus
- ✅ Semantic search with proper metadata
- ✅ Text content retrieval from PostgreSQL  
- ✅ RAG context integration in chat
- ✅ System prompt enhancement with document content
- ✅ Graceful fallback when no context found

### Endpoints Çalışır Durumda:
- `POST /upload` - Dosya yükleme + otomatik embedding
- `POST /embedding/rag/retrieve` - Manual RAG context çekme
- `POST /embedding/rag/complete` - RAG + LLM completion
- `POST /chat` - RAG-enhanced chat (API key ile)

## Çalışanlar
- Backend API ve temel endpoint'ler (sohbet, belge yükleme, model yönetimi, healthcheck)
- **Tam RAG Pipeline** - Upload'tan chat'e kadar complete flow
- Milvus, Redis, PostgreSQL entegrasyonları
- Migration sırası ve servis başlatma süreçleri otomatikleştirildi
- Test runner ve izole test ortamı (docker-compose.test.yml) kuruldu
- Build ve test süreçleri optimize edildi
- **Vector search ve context retrieval** tamamen çalışır durumda
- **Chat-RAG integration** test edildi ve doğrulandı

## Eksikler
- Frontend React UI tam implementasyonu
- File parsing pipeline'ına DOCX desteği
- Document management interface
- User-specific document isolation
- Advanced RAG features (filtering, relevance tuning)
- Production environment configurations
- Comprehensive error handling ve monitoring
- **Yeni:** Tab'lı ve sidebar'lı modern chat arayüzü, component breakdown'unun React ile uygulanması
- **🟦 Frontend-Backend Entegrasyon Eksikleri:**
    - Model ve dosya yönetimi için eksik olan `DELETE` ve `PUT` endpointleri backend'de tamamlanmalı.
    - Frontend'de API servis katmanı ve state yönetimi eksik, tamamlanmalı.
    - Chat geçmişi için ek endpoint gerekiyorsa planlanmalı.
    - Dockerfile ve docker-compose entegrasyonu tamamlanmalı.
- **🟧 Entegrasyon Problemleri:**
    - Frontend ve backend API'ları arasında tam uyum sağlanamadı.
    - Build ve deployment sırasında çıkan hatalar (örn. script eksikliği, yanlış build yolu, port çakışması) tekrar gözden geçirilmeli.
    - API endpoint ve veri modeli uyumsuzlukları giderilmeli.
    - Docker network ve environment ayarları kontrol edilmeli.
- **🟧 UI/UX ve Entegrasyon Eksikleri:**
    - Chat input bar'ın sabitlenmemesi
    - Modellerin backend'den alınamaması
    - Model eklemenin prompt ile yapılması
    - Dosya eklemede drag & drop eksikliği
    - Chat ekranında model seçimi eksikliği
    - **API endpoint uyumsuzlukları ve eksik dosya listeleme:**
        - Model ekleme için /model/create endpointi kullanılmalı
        - Dosya yükleme için /upload endpointi kullanılmalı
        - Backend'de GET /files endpointi eksik

## Bilinen Sorunlar
- API key requirement for LLM calls (OpenRouter/OpenAI)
- Milvus container restart dependency
- Large document processing optimization needed
- Memory usage optimization for embedding generation
- Frontend-backend integration pending
- **🟧 Entegrasyon ve Dağıtım Sorunları:**
    - Port çakışması, build script eksikliği, Vite/React build çıktısı yolu, package.json konumu gibi teknik detaylar entegrasyon sürecini yavaşlatıyor.
    - Docker imajı çekme ve internet bağlantısı sorunları yaşanabiliyor.
    - API endpoint'lerinin frontend ile tam uyumlu olmaması, veri modeli farklılıkları ve hata yönetimi eksiklikleri entegrasyonun önünde engel oluşturuyor.

## 🎯 Major Milestone Achieved
**RAG entegrasyonu tamamen tamamlandı ve test edildi!** Kullanıcılar artık belge yükleyip, bu belgeler hakkında LLM'ler ile sohbet edebilirler. Sistem otomatik olarak ilgili belge parçalarını bulup, LLM'e context olarak sağlıyor. 

### 2025-06-11 Güncelleme
- Model management arayüzü ve API entegrasyonu backend ile tam uyumlu hale getirildi.
- Model ekleme, güncelleme ve silme işlemleri backend'de sorunsuz çalışıyor.
- Formda tüm zorunlu ve opsiyonel alanlar backend ile uyumlu şekilde işleniyor.
- Model güncelleme sırasında model_id hatası giderildi.
- Şu anda model management tarafı stabil durumda.
- Ancak UI tarafında ve diğer servislerin entegrasyonlarında halen problemler mevcut.
- Bundan sonraki adım: UI ve diğer servis entegrasyonlarındaki sorunlar adım adım çözülecek. 

## Model Management
- Model yönetimi için accordion yapısı, backend ile tam uyumlu şekilde tamamlandı.
- Zorunlu ve opsiyonel alanlar iki sütunlu, responsive grid ile ayrıldı.
- UI/UX modern ve kullanılabilir durumda.
- Orta vadede: UI/UX için ek görsel ve etkileşimsel düzenlemeler planlanıyor.

## File Management
- File Management sayfasında da benzer iki sütunlu, responsive ve modern form/grid düzeni yapılacak.
- Dosya ekleme, silme, detay gösterimi için UI/UX iyileştirmeleri ve fonksiyonel entegrasyonlar sırada.

## Chat Entegrasyonu
- Chat entegrasyonu şu an çalışmıyor.
- Chat ekranı ve servis entegrasyonu ile ilgili eksikler giderilecek.
- UI/UX ve state yönetimi iyileştirilecek.

## Genel
- Tüm sayfalarda component'lerin ekrana göre scale olması ve modern görünüm için responsive düzenlemeler orta vadeli planda.
- Geliştirme adım adım ilerliyor, memory-bank üzerinden takip edilecek. 

# progress - Context Window Yönetimi İlerlemesi

## Şu Ana Kadar Yapılanlar
- Prompt büyümesi ve context window taşması engellendi.
- Token limiti aşılırsa eski mesajlar baştan siliniyor.

## Planlananlar
- Gerçek token hesaplama entegrasyonu.
- Eski mesajların otomatik özetlenmesi.
- Kullanıcıya context window uyarısı.
- Gelişmiş context ve RAG yönetimi stratejileri. 

# Proje İlerleme Durumu (Progress)

- Uzun vadeli hibrit arama ve gelişmiş RAG değerlendirme/loglama altyapısı planı oluşturuldu ve memory bank'e kaydedildi.
- Mimari şema memory bank'te güncellendi.
- Modül iskeleti oluşturuldu ve memory bank'e kaydedildi.
- Sıradaki adım: unstructured entegrasyonu, embedding pipeline güncellemesi, hibrit arama ve gelişmiş loglama altyapısının uygulanması. 

# Proje Düzenleme ve İyileştirme Planı (2024)

## 1. Bağımlılık ve Dockerfile Optimizasyonu
- Gereksiz ve çakışan paketlerin requirements.txt'den temizlenmesi
- Sadece production için gerekli ana paketlerin bırakılması
- Test/dev/lint bağımlılıklarının ayrılması (gerekirse requirements-dev.txt'ye taşınması)
- Dockerfile'ın layer/cache dostu ve hızlı build edecek şekilde optimize edilmesi
- Poppler, tesseract, NLTK gibi ek sistem bağımlılıklarının doğru sırada kurulması
- Numpy, packaging, langchain, unstructured gibi paketlerin uyumlu sürümlerinin sabitlenmesi

## 2. Dosya İşleme ve Performans İyileştirmeleri
- Unstructured ile PDF işleme sırasında encoding hatalarının önlenmesi (dosya okuma/decode işlemlerinin gözden geçirilmesi)
- PDF işleme hızının artırılması:
    - Varsayılan olarak fast/auto strategy kullanılması
    - OCR'ın sadece gerektiğinde (görsel tabanlı PDF) devreye alınması
    - Dosya boyutu ve sayfa sayısına göre dinamik işleme stratejisi belirlenmesi
- Dosya yükleme ve chunking pipeline'ında loglama ve hata yönetiminin iyileştirilmesi

## 3. Kod Temizliği ve Modülerlik
- Gereksiz veya tekrar eden kodların temizlenmesi
- Parametrelerin fonksiyonlara tekil ve doğru şekilde aktarılması (ör. infer_table_structure hatası gibi)
- Testlerin ayrıştırılması ve test bağımlılıklarının izole edilmesi
- Kodun okunabilirliğinin ve sürdürülebilirliğinin artırılması

## 4. Dokümantasyon ve Süreç Takibi
- README.md ve progress.md dosyalarının güncellenmesi
    - Son yapılan değişikliklerin ve mevcut mimarinin net şekilde aktarılması
    - Bilinen sorunlar ve çözüm önerilerinin eklenmesi
    - Kullanım ve deploy talimatlarının sadeleştirilmesi
- Geliştirici onboarding'i için kısa bir "Nasıl başlarım?" rehberi eklenmesi

## 5. İzleme ve Gelişmiş Loglama
- Dosya işleme, chunking ve embedding pipeline'larında detaylı loglama
- Hataların ve yavaş noktaların kolayca tespit edilebilmesi için temel metriklerin eklenmesi

## 6. Sonraki Adımlar ve Geliştirme
- RAG pipeline'ının uçtan uca test edilmesi
- Frontend-backend entegrasyonunun stabil çalıştığının doğrulanması
- Geliştirici ve kullanıcıdan gelen yeni hata/feature taleplerinin backlog'a eklenmesi

### Öncelik Sıralaması
1. Bağımlılık ve Dockerfile optimizasyonunun tamamlanması
2. Dosya işleme ve performans iyileştirmeleri
3. Kod temizliği ve modülerlik
4. Dokümantasyonun güncellenmesi
5. İzleme ve loglama eklenmesi
6. Sonraki adımların planlanması ve backlog'un güncellenmesi 

### Backend
- **✅ Endpointler (GET /files, model CRUD vb.)** - MVP için yeterli düzeyde mevcut
- **🟧 Diğer eksikler ve iyileştirmeler** - Devam ediyor (dosya işleme pipeline'ında encoding ve hız iyileştirmeleri, hybrid search, semantic filtering, A/B test, gelişmiş loglama ve monitoring henüz tam entegre değil) 

## 🚧 v0.4 Planlanan Geliştirmeler

### Dosya Yükleme ve İşleme Sırasında Progress Feedback
- Kullanıcıya dosya yükleme ve işleme pipeline'ında adım adım ilerleme gösterecek progress feedback sistemi eklenecek.
- Backend'de her upload işlemi için pipeline adımlarında progress objesi güncellenecek (örn. Redis veya memory).
- Progress sorgulama endpoint'i (GET /upload/status/{file_id}) eklenecek.
- Frontend'de progress bar ve adım adım durum göstergesi ile kullanıcıya anlık bilgi verilecek.
- Gelişmiş UX için WebSocket/SSE ile gerçek zamanlı bildirim opsiyonu değerlendirilecek.
- Bu özellik v0.4 ile birlikte devreye alınacak, v0.3'te mevcut değildir. 

# PDF Extraction & Chunking Migration Planı (Unstructured'dan Tamamen Çıkış)

## 1. Unstructured Bağımlılığını ve Kodunu Tespit Et
- requirements.txt ve requirements.txt.backup dosyalarında `unstructured` ve ilgili alt paketleri (unstructured[all], unstructured[local-inference], vs.) kaldırılacak.
- src/backend/services/file/unstructured_adapter.py ve diğer dosyalarda:
  - `from unstructured...` ile başlayan tüm importlar kaldırılacak.
  - `partition_pdf`, `partition_docx`, `partition_html`, `partition`, `partition_text` gibi fonksiyon çağrıları kaldırılacak.
  - Unstructured'a özel chunking, cleaning, extraction fonksiyonları kaldırılacak.

## 2. Koddan Unstructured'ı Kaldır
- requirements.txt ve varsa Dockerfile'dan unstructured ile ilgili satırlar silinecek.
- unstructured_adapter.py dosyası tamamen kaldırılacak veya PyMuPDF/pdfplumber tabanlı yeni extraction fonksiyonları ile değiştirilecek.
- Diğer modüllerde (ör. service.py, parent_child_chunker.py) unstructured fonksiyonlarına yapılan tüm çağrılar kaldırılacak veya refactor edilecek.

## 3. Yeni Hibrit Extraction/Chunking Pipeline'ı
- **TOC Extraction:** PyMuPDF (`fitz`) ile `doc.get_toc()` kullanılarak nested başlık-parent-child yapısı çıkarılacak.
- **Başlık ve Paragraf Extraction:** PyMuPDF ile sayfa, blok, font, bold, numaralandırma analizine dayalı başlık tespiti yapılacak. Başlıklar parent, altındaki paragraflar/cümleler child olarak atanacak.
- **Tablo, Görsel, Liste Extraction:** pdfplumber ile tablo (`page.extract_tables()`), görsel (`page.images`), liste ve paragraf extraction yapılacak. Tablolar ve görseller ilgili parent başlık altına child olarak eklenecek.
- **Fallback:** Hiç başlık yoksa, her sayfa parent chunk olarak atanacak, altındaki tüm metin blokları child olarak eklenecek.

## 4. Kodda Değişiklik Yapılacak Dosyalar
- requirements.txt: unstructured ve alt bağımlılıkları kaldırılacak, pymupdf, pdfplumber, camelot, tabula gibi yeni bağımlılıklar eklenecek.
- Dockerfile: Gerekirse yeni bağımlılıklar için sistem paketleri eklenecek (ör. poppler-utils, ghostscript).
- src/backend/services/file/unstructured_adapter.py: Dosya tamamen kaldırılacak veya yeni extraction fonksiyonları ile değiştirilecek.
- src/backend/services/file/service.py: `parse_document` fonksiyonu yeni adapter'a yönlendirilecek. Unstructured'a özel kodlar kaldırılacak.
- src/backend/services/chunking/parent_child_chunker.py: Başlık tespiti ve parent-child mapping fonksiyonları yeni extraction yapısına göre güncellenecek.
- Testler: Extraction ve chunking testleri yeni pipeline'a göre güncellenecek.

## 5. Yeni Extraction Adapter (Örnek Akış)
- PyMuPDF ile TOC extraction ve başlık-parent-child mapping
- pdfplumber ile tablo, görsel, paragraf extraction
- Kodun modüler ve kolay değiştirilebilir olması sağlanacak

## 6. Test ve Validasyon
- Yeni extraction pipeline ile örnek PDF'lerde başlık-parent-child hiyerarşisi, paragraf, tablo, görsel, liste extraction, chunk mapping ve DB insert işlemleri test edilecek.
- Tüm extraction fonksiyonlarının unit ve entegrasyon testleri güncellenecek.

## 7. Dokümantasyon ve README Güncellemesi
- README.md ve docs/ altında extraction pipeline'ın yeni akışı, kullanılan kütüphaneler ve örnek kodlar güncellenecek.
- Eski Unstructured'a dair tüm referanslar kaldırılacak.

## 8. Geriye Dönük Uyumluluk ve Temizlik
- Eski migration fonksiyonları ve Unstructured'a dair helper'lar tamamen silinecek.
- Gerekirse eski extraction sonuçları yeni pipeline ile yeniden üretilecek.

---

## Notlar
- Unstructured ile yapılması planlanan tüm değişiklikler ve referanslar bu migration ile kaldırılmıştır.
- Yeni extraction pipeline tamamen açık kaynak ve sürdürülebilir kütüphanelerle (PyMuPDF, pdfplumber, vs.) kurulacaktır. 