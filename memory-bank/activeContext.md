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