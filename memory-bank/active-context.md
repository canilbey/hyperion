# Aktif Bağlam (Active Context)

- unstructured ile ham veri işleme ve parent-child chunking
- Multilingual embedding modeli ile vektör üretimi (Milvus)
- Hibrit arama: BM25 (örn. Elasticsearch) + vektör arama + cross-encoder reranking
- Parent-child retrieval: Arama child chunk'larda, bağlam parent chunk'ta
- Gelişmiş loglama ve RAGAs ile otomatik değerlendirme
- Analitik veri gölü ve dashboard ile sürekli analiz ve optimizasyon
- Modül iskeleti: unstructured_adapter, parent_child_chunker, embedding pipeline, bm25_service, vector_service, fusion, rerank, hybrid_search, parent_child_retriever, ragas_adapter, logger, feedback, dashboard_api 

# RAG Pipeline Geliştirme Yol Haritası ve İyileştirme Kayıtları (2025-06-15)

## 1. Şu Ana Kadar Yapılan Temel İyileştirmeler
- Unstructured ile dosya parsing pipeline'ı tamamen yeniden yazıldı, PDF, TXT, HTML için uygun parser seçimi eklendi.
- PDF dosyaları için magic number ve uzantı ile güvenli tespit ve sadece partition_pdf ile işleme.
- Tüm chunk'ların text içeriği normalize ve temizleniyor (unicode normalization, printable filtering, safe utf-8).
- NLTK punkt_tab runtime'da sadece ilk ihtiyaçta indiriliyor.
- Parent-child chunking algoritması, başlıksız dokümanlar ve fallback durumları için güçlendirildi.
- Embedding pipeline'da batch ve text cleaning uygulandı.
- DB insert ve response işlemlerinde encoding hataları tamamen önlendi.
- Hybrid search, semantic filtering ve A/B test için altyapı hazırlıkları başlatıldı.

## 2. Geliştirme Yol Haritası ve Planı

### 1️⃣ Başlık ve Section Algoritması
- Regex + heuristic ile başlık tespiti, ML tabanlı section splitter araştırması.
- PDF/HTML'de görsel ve yapısal ipuçları ile section extraction.
- Parent chunk'lara section_level, section_type metadata eklenmesi.

### 2️⃣ Index Optimizasyonu (PostgreSQL)
- child_chunks(parent_id), parent_chunks(document_id) index'leri mevcut.
- Ek olarak: child_chunks(type), parent_chunks(title), metadata için GIN index.
- Büyük tablolarda partitioning ve düzenli VACUUM/ANALYZE.

### 3️⃣ Milvus Index Tipi
- Küçük veri için FLAT, büyük veri için IVF_FLAT, HNSW gibi index tipleri.
- Parametre tuning (nlist, nprobe, efConstruction, efSearch).
- Farklı index tiplerinde benchmark ve latency ölçümü.

### 4️⃣ Upload Progress & Feedback
- Frontend'de chunked upload ve progress bar.
- Backend'de pipeline adımlarında progress event'leri (WebSocket/SSE/polling).
- /upload/status/{file_id} endpoint'i ile anlık durum.

### 5️⃣ Hybrid Search
- BM25 (Elasticsearch) + Milvus vektör arama + skor fusion.
- İlk 20 sonucu cross-encoder ile rerank.
- /search/hybrid endpoint'i.

### 6️⃣ Semantic Filtering
- Dil tespiti, chunk tipi, minimum bilgi eşiği ile filtreleme.
- Stopword/noise filtering.

### 7️⃣ A/B Test Altyapısı
- Kullanıcı/dosya bazında pipeline varyantı atama.
- Her sorgu ve yanıt için varyant, skor, feedback loglama.
- Sonuçları dashboard ile görselleştirme.

## 3. Diğer Teknik Notlar
- Tüm pipeline'da encoding ve text temizlik fonksiyonları zorunlu.
- PDF gibi binary formatlarda asla text parser kullanılmıyor.
- Her adımda fallback ve hata toleransı var.
- Geliştirici ve kullanıcı deneyimi için monitoring, logging ve test otomasyonu öncelikli.

---
Bu yol haritası ve kayıtlar, Hyperion RAG platformunun sürdürülebilir ve ölçeklenebilir gelişimi için referans olarak kullanılacaktır. 