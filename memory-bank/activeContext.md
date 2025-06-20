# Hyperion - Güncel Durum ve Amaç

## Projenin Amacı
Hyperion, kullanıcıların belge yükleyip, bu belgelerden LLM destekli, bağlama duyarlı yanıtlar alabileceği, modüler ve ölçeklenebilir bir platformdur. Platformun temel hedefi, büyük ve karmaşık belge koleksiyonlarından hızlı, doğru ve bağlama uygun bilgiye erişimi mümkün kılmaktır.

## Güncel Durum (2024-06)
- Projede PDF parsing için unstructured kütüphanesinden custom parsing sistemine geçiş süreci başlatılmıştır.
- Yeni custom sistemde, PyMuPDF (fitz) ve pdfplumber ile başlık, section, tablo, görsel, liste, cümle ve paragraf bazlı parent-child chunk extraction yapılmaktadır.
- Her chunk'a detaylı metadata eklenmekte, fallback ve hata toleransı sağlanmaktadır.
- RAG pipeline, frontend-backend entegrasyonu, model ve dosya yönetimi, modern React arayüzü ve production-ready mimari büyük ölçüde tamamlanmıştır.
- Geliştirme odağı, gelişmiş belge işleme, kullanıcı deneyimi, performans optimizasyonu ve yeni özelliklerin entegrasyonuna kaymıştır.

---
# Active Context

## Şu Anki Odak
- **✅ TAMAMLANDI:** libGL.so.1 hatası çözümü - OpenCV bağımlılığından kaçınma
- **✅ TAMAMLANDI:** unstructured kütüphanesinin optimal kullanımı
- **✅ TAMAMLANDI:** PDF parsing için en verimli yöntem (partition.auto + strategy optimization)
- **✅ TAMAMLANDI:** Docker container optimizasyonu
- Frontend React UI geliştirme ve backend entegrasyonu
- Document management interface tasarımı
- User-specific document isolation implementasyonu
- Advanced RAG features (multi-document querying, filtering)
- Production environment configurations ve deployment hazırlığı
- Performance optimizations (embedding caching, vector index tuning)
- API rate limiting ve security hardening

## Son Yapılanlar
- **🎉 RAG Pipeline Tamamen Tamamlandı** - End-to-end RAG sistemi çalışır durumda
- **✅ Chat-RAG Integration** - Chat service'e otomatik RAG context ekleme
- **✅ Vector Search Fix** - Milvus output_fields ile metadata retrieval çözüldü
- **✅ Async RAG Service** - PostgreSQL integration ile text content çekme
- **✅ Error Handling** - HTTPException import ve graceful fallbacks eklendi
- **✅ Milvus Tensor Support** - Query embedding format conversion implemented
- **✅ Context Assembly** - PostgreSQL'den actual text content çekme sistemi
- **✅ Debug Logging** - RAG pipeline monitoring ve troubleshooting
- **✅ End-to-End Testing** - File upload → embedding → search → chat flow doğrulandı
- **✅ Modern Frontend UI** - React + UnoCSS ile minimal, tab'lı, sidebar'lı arayüz başarıyla çalışıyor. Tüm eski config ve dosya çakışmaları giderildi. Ana içerik alanı ChatGPT benzeri chat, tıklanabilir model ve dosya listeleri, detay panelleri ile tamamlandı.
- **✅ File Management Backend-Frontend Entegrasyonu** - Dosya yükleme, listeleme ve silme işlemleri backend ve frontend arasında uçtan uca entegre edildi. Migration, model ve servis güncellemeleri tamamlandı.

## RAG Pipeline Başarıları
### Çalışan Flow:
```
📝 User Upload → 📄 File Parse → 🧠 Embedding Gen → 🗄️ Milvus Store → 💬 Chat Query → 🔍 Vector Search → 📚 Context Retrieval → 🤖 LLM Enhancement → 📤 Response
```

### Test Edilmiş Özellikler:
- ✅ PDF/TXT file upload with automatic embedding generation
- ✅ Vector storage in Milvus with proper metadata
- ✅ Semantic search returning actual document content
- ✅ RAG context automatic integration in chat system
- ✅ System prompt enhancement with document context
- ✅ Graceful fallback when no relevant context found
- ✅ Modern frontend UI ile tüm componentler ve layout çalışıyor

## Sonraki Adımlar
- **Frontend UX Geliştirmeleri** - File management arayüzünde kullanıcı deneyimi iyileştirilecek (sidebar'da sade liste, ana panelde akordiyon detay, silme butonu için uygun ikon, responsive tasarım).
- **Backend Entegrasyonu** - Gerçek veri ile chat, model ve dosya yönetimi, API bağlantıları
- **Advanced RAG Features** - Document filtering, relevance scoring, multi-doc querying
- **Performance Optimization** - Embedding caching, vector index tuning, chunk size optimization
- **Production Readiness** - Environment configs, security hardening, monitoring
- **Document Management** - User-specific document isolation ve metadata management
- **API Enhancements** - Rate limiting, error handling, response optimization
- **Yeni:**
    - Sidebar: Model yönetimi (oluştur, düzenle, sil), dosya yönetimi (yükle, chunklar), yeni chat oluşturma, chat listesi
    - Ana içerik: Tab'lı yapı (Chat, Model Yönetimi, Dosya Yönetimi)
    - Chat tabında sadece model seçimi ve chat alanı
    - Responsive, minimal ve modern component breakdown'unun React ile uygulanması
    - **Modern frontend arayüzü tamamlandıktan sonra:** Backend API entegrasyonu, dosya yükleme ve chat ile gerçek veri akışı

## Teknik Notlar
- RAG sistemi production-ready seviyede çalışıyor
- Milvus container restart dependency çözülmesi gerekiyor
- Large document processing için memory optimization planlanmalı
- Frontend-backend integration için API documentation tamamlanmalı
- User authentication ile document isolation entegrasyonu yapılmalı

---
# Teknik Yol Haritası ve Geliştirme Planı

## 1. Başlık ve Section Algoritması
- Regex + heuristic ile başlık tespiti, ML tabanlı section splitter araştırması.
- PDF/HTML'de görsel ve yapısal ipuçları ile section extraction.
- Parent chunk'lara section_level, section_type metadata eklenmesi.

## 2. Index Optimizasyonu (PostgreSQL)
- child_chunks(parent_id), parent_chunks(document_id) index'leri mevcut.
- Ek olarak: child_chunks(type), parent_chunks(title), metadata için GIN index.
- Büyük tablolarda partitioning ve düzenli VACUUM/ANALYZE.

## 3. Milvus Index Tipi
- Küçük veri için FLAT, büyük veri için IVF_FLAT, HNSW gibi index tipleri.
- Parametre tuning (nlist, nprobe, efConstruction, efSearch).
- Farklı index tiplerinde benchmark ve latency ölçümü.

## 4. Upload Progress & Feedback
- Frontend'de chunked upload ve progress bar.
- Backend'de pipeline adımlarında progress event'leri (WebSocket/SSE/polling).
- /upload/status/{file_id} endpoint'i ile anlık durum.

## 5. Hybrid Search
- BM25 (Elasticsearch) + Milvus vektör arama + skor fusion.
- İlk 20 sonucu cross-encoder ile rerank.
- /search/hybrid endpoint'i.

## 6. Semantic Filtering
- Dil tespiti, chunk tipi, minimum bilgi eşiği ile filtreleme.
- Stopword/noise filtering.

## 7. A/B Test Altyapısı
- Kullanıcı/dosya bazında pipeline varyantı atama.
- Her sorgu ve yanıt için varyant, skor, feedback loglama.
- Sonuçları dashboard ile görselleştirme.

## 8. Diğer Teknik Notlar
- Tüm pipeline'da encoding ve text temizlik fonksiyonları zorunlu.
- PDF gibi binary formatlarda asla text parser kullanılmıyor.
- Her adımda fallback ve hata toleransı var.
- Geliştirici ve kullanıcı deneyimi için monitoring, logging ve test otomasyonu öncelikli.

---
Bu yol haritası ve kayıtlar, Hyperion RAG platformunun sürdürülebilir ve ölçeklenebilir gelişimi için referans olarak kullanılacaktır.

# activeContext - Güncel Durum ve Planlar

## Şu Anki Durum
- Sadece en son user mesajı için RAG context ekleniyor.
- LLM'ye gönderilecek mesajların toplam token sayısı yaklaşık olarak kelime sayısının iki katı ile tahmin ediliyor.
- Modelin context window/token limiti aşılırsa, en eski mesajdan başlayarak mesajlar otomatik olarak siliniyor.

## Yol Haritası
- Daha hassas token hesaplama (ör. tiktoken ile).
- Eski mesajların otomatik özetlenmesi.
- Kullanıcıya context window dolduğunda uyarı.
- Gelişmiş context window ve RAG yönetimi stratejileri.

# Arama Sonuçlarının Gösterimi - Mevcut Durum ve Plan

## Mevcut Durum
- Backend ve API, arama sonuçlarında chunk metni, skor ve zengin metadata (sayfa numarası, dosya adı, chunk_index, offset, vs.) dönebiliyor.
- Frontend'de genellikle sadece metin ve skor gösteriliyor, metadata çoğunlukla kullanılmıyor.

## Planlanan İyileştirmeler
1. **API response formatı netleştirilecek ve dökümante edilecek.**
2. **Frontend'de arama sonucu kartları, metadata (sayfa numarası, dosya adı, chunk_index, konum, vs.) ile zenginleştirilecek.**
3. **Kullanıcıya chunk'ın kaynağı ve konumu (örn. PDF sayfası) gösterilecek, "Kaynağı Gör" gibi butonlar eklenecek.**
4. **Ekstra UX iyileştirmeleri: Tooltip, detay modalı, chunk highlight, filtreleme/sıralama, metadata export, chunk gruplama.**

## Hedef
- Chunk'ın metniyle birlikte, sayfa numarası, dosya adı, chunk konumu gibi tüm metadata'nın kullanıcıya şeffaf ve kullanışlı şekilde sunulması.
- Kullanıcı deneyiminin ve arama sonuçlarının anlamlılığının artırılması.

# 2025-06-15: Modüler RAG Pipeline Servis Mimarisi ve Entegrasyon Planı

## Hedefler
- Her ana işlev (parsing, chunking, embedding, search) ayrı bir servis ve klasör olarak yapılandırılacak.
- Her servis kendi bağımlılıklarını, yardımcı fonksiyonlarını ve testlerini içerecek.
- Servisler arası iletişim net, sade ve API tabanlı olacak (gerekirse async/await ile).
- Gelecekte yeni dosya tipleri veya chunking stratejileri kolayca eklenebilecek.
- Unstructured ve diğer bağımlılıklar eksiksiz kurulacak.
- Her servis için logging, hata yönetimi ve test altyapısı olacak.

## Klasör Yapısı

src/
  backend/
    services/
      file_parsing/
        parser.py           # partition.auto, fallback, dosya tipi tespiti
        tests/
      chunking/
        chunker.py          # başlık bazlı, sabit boyutlu, vs. chunking
        utils.py
        tests/
      embedding/
        embedder.py         # sentence-transformers, model yönetimi
        utils.py
        tests/
      search/
        searcher.py         # Milvus, metadata, hybrid search
        utils.py
        tests/
    routers/
      file_router.py
      chunking_router.py
      embedding_router.py
      search_router.py
    ...

## Servis Sorumlulukları
- **file_parsing:** Dosya tipi tespiti, partition.auto ile parsing, fallback, temizlik, yeni formatlar için genişletilebilirlik
- **chunking:** Başlık bazlı/sabit boyutlu/semantik chunking, metadata, birleştirme/bölme, test
- **embedding:** Her chunk için embedding, model yönetimi, metadata
- **search:** Sorgu embedding'i ile Milvus arama, metadata ile parent chunk çekme, hybrid search, LLM prompt hazırlama

## Entegrasyon Akışı
1. Kullanıcı dosya yükler → file_parsing servisi parse eder
2. Element listesi → chunking servisine aktarılır, chunk'lara bölünür
3. Chunk listesi → embedding servisine aktarılır, embedding'ler üretilir ve Milvus'a kaydedilir
4. Kullanıcı sorgusu → search servisine gelir, arama yapılır, en alakalı chunk ve parent chunk bulunur
5. Sonuçlar → LLM'ye prompt olarak hazırlanır ve kullanıcıya döndürülür

## Gereksinimler
- Python: unstructured[pdf,docx,html,image,eml], PyPDF2, sentence-transformers, pymilvus, elasticsearch, langchain, ...
- Sistem: poppler-utils, libmagic1, tesseract-ocr, libxml2-dev, libxslt1-dev, file
- NLTK data: punkt, averaged_perceptron_tagger (runtime'da otomatik indirme)

## Dinamik Dosya Tipi Yönetimi
- Uzantı + magic number + partition.auto ile tespit
- Gerekli unstructured eklentisi yüklü değilse log ve kullanıcıya uyarı
- Gelecekte yeni formatlar için kolayca yeni parser eklenebilir

## Servisler Arası API/Interface
- file_parsing.parser.parse(file_path) -> List[Element]
- chunking.chunker.chunk(elements) -> List[Chunk]
- embedding.embedder.embed(chunks) -> List[Embedding]
- search.searcher.search(query_embedding) -> List[SearchResult]

## Test ve Geliştirilebilirlik
- Her servis için tests/ klasörü ve örnek testler
- Servisler arası bağımlılık minimumda tutulur
- Her servis kendi başına test edilebilir ve geliştirilebilir

## Geleceğe Dönük Genişletilebilirlik
- Yeni dosya tipleri için yeni parsing modülleri
- Farklı chunking stratejileri kolayca entegre edilebilir
- Embedding ve search servisleri yeni modeller ve vektör veritabanları ile genişletilebilir

## Akış Diyagramı

File Upload → file_parsing → chunking → embedding → search → LLM Prompt/Response 

## 2025-06-19: Paragraf Bazlı Chunking ve Hybrid Search Geliştirme Planı

### Paragraf Bazlı Chunking
- Chunk'lar paragraf bazlı olacak, 500 token sınırı uygulanacak.
- Uzun paragraflar cümle bazında bölünecek, chunk'lar arasında son 1-2 cümle overlap olacak.
- Token hesaplama için tiktoken veya benzeri tokenizer kullanılacak.
- Her chunk'a detaylı metadata eklenecek.

### Hybrid Search
- BM25 (Elasticsearch) + Milvus vektör arama birlikte kullanılacak.
- `/search/hybrid` endpoint'i ile hem BM25 hem vektör arama sonuçları alınacak.
- Sonuçlar skor bazında normalize edilip birleştirilecek (fusion).
- İlk 10-20 sonuç cross-encoder ile rerank edilebilecek.
- Sonuçlar chunk metni, skor, kaynak ve metadata ile frontend'e dönecek. 

## 2025-06-20: Advanced RAG - Semantic + Hybrid Search Pipeline Geliştirmesi

### 1. Semantic Search Akışı
- Kullanıcı sorgusu embedding'e dönüştürülüp Milvus'ta arama yapılır.
- İlk etapta en iyi 5 child chunk alınır.
- Eğer bu 5 child chunk'tan herhangi birinin similarity skoru 0.1'den büyükse:
    - En yüksek skora sahip child chunk'ın parent'ı alınır.
    - Bu parent chunk'ın içeriği LLM'ye (veya hybrid search karşılaştırmasına) gönderilir.
- Eğer 5 sonuçtan hiçbiri 0.1'in üstünde değilse:
    - En iyi 20 child chunk alınır.
    - 0.08'in üstünde similarity skoruna sahip child chunk'lar arasından en iyi 3 tanesinin parent'ı seçilir.
    - Ortak parent varsa, aynı parent tekrar tekrar işlenmez (her parent bir kez dahil edilir).
- Seçilen parent chunk'ların içeriği, LLM'ye prompt olarak veya hybrid search karşılaştırmasına gönderilir.

### 2. Hybrid Search Akışı
- Kullanıcı sorgusu hem BM25 (Elasticsearch) hem de vektör arama (Milvus) ile sorgulanır.
- BM25 ve vektör arama sonuçları normalize edilip fusion algoritması ile birleştirilir.
- Semantic search pipeline'ından gelen parent chunk'lar, hybrid search karşılaştırmasına dahil edilir.
- İlk 10-20 sonuç cross-encoder ile rerank edilebilir.
- Sonuçlar chunk metni, skor, kaynak, dosya adı, sayfa numarası gibi metadata ile frontend'e döner.
- Sonuçlarda parent chunk tekrarları engellenir, her parent sadece bir kez işlenir.

### 3. Teknik Notlar ve Geliştirme Adımları
- Milvus arama fonksiyonu, similarity threshold ve parent toplama mantığı ile güncellenecek.
- Parent chunk retrieval ve tekrar engelleme için yardımcı fonksiyonlar eklenecek.
- BM25/Elasticsearch entegrasyonu ve fusion algoritması geliştirilecek.
- `/search/hybrid` endpoint'i ile yeni akış frontend'e açılacak.
- Testler: Eşik değerleri, parent toplama, tekrar engelleme ve fusion mantığı için birim ve entegrasyon testleri yazılacak. 

## Current Limitations & Future Improvements

### OCR Integration Need
- Mevcut sistem sadece metin tabanlı PDF'leri işleyebiliyor
- Taranan belgeler ve görüntü bazlı PDF'ler için OCR gerekiyor
- Özellikle eski dokümanlar ve resmi belgeler için önemli

### Planned Solution
1. **Phase 1: Tesseract OCR**
   - Açık kaynak, self-hosted çözüm
   - Temel görüntü işleme
   - Türkçe desteği

2. **Phase 2: Cloud Integration**
   - Google/Azure OCR servisleri
   - Yüksek doğruluk
   - Ölçeklenebilirlik

3. **Phase 3: Optimization**
   - Asenkron işleme
   - Önbellekleme
   - Monitoring

### Implementation Timeline
- Planning: Completed
- Phase 1: Q2 2024
- Phase 2: Q2-Q3 2024
- Phase 3: Q3 2024

### Success Metrics
- OCR doğruluk oranı >90%
- Sayfa başına işlem süresi <30 sn
- Hata oranı <1% 