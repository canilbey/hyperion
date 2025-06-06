# Hyperion Pipeline Mevcut Durum Raporu

## 1. Uçtan Uca Pipeline

### File Upload
- **Endpoint:** POST /upload (src/backend/main.py)
- Kullanıcı dosya yükler, dosya FileService ile kaydedilir, metadata PostgreSQL'e yazılır.

### File Parsing
- **Mevcut Durum:** PDF ve TXT dosya tipleri için otomatik parsing ve metin çıkarımı mevcut. DOCX ve diğer formatlar için geliştirme devam ediyor.
- **Eksik:** DOCX gibi yeni dosya tipleri için parser ve otomatik metin çıkarımı gerekmekte.

### Embedding
- **Endpoint:** POST /embedding/embed (src/backend/routers/embedding.py)
- Metinler embedding'e çevrilir, Milvus'a ve metadata ile birlikte kaydedilir.

### Vector Storage & Query
- **Storage:** Embedding'ler Milvus'a, metadata PostgreSQL'e kaydedilir.
- **Query:** POST /embedding/search veya /search ile embedding tabanlı arama yapılır.

### Model Creation
- **Endpoint:** POST /model/create (src/backend/main.py)
- Model konfigürasyonu PostgreSQL'de saklanır.

### Chat & RAG
- **Chat:** POST /chat, /chat/{identifier}, GET /chats, GET /chats/{identifier}/messages
- **RAG:** POST /embedding/rag/retrieve, /embedding/rag/complete
- Sohbetler ve mesajlar PostgreSQL'de, oturumlar Redis'te tutulur.

### Veri Tabanı ve Cache Kullanımı
- **Milvus:** Embedding ve vektör arama
- **PostgreSQL:** Metadata, dosya, model, sohbet, mesaj
- **Redis:** Oturum ve hızlı erişim (opsiyonel)

### Test & Otomasyon
- Test runner ve izole test ortamı (docker-compose.test.yml) ile tüm ana servislerin entegrasyonu otomatik olarak test ediliyor
- API key ile korunan endpointler ve dosya yükleme endpointi için otomatik testler mevcut
- Test runner imajında eksik bağımlılıklar (ör. psycopg2) eklendi
- Build ve test süreçleri optimize edildi, gereksiz build işlemleri önlendi
- CI/CD entegrasyonu için hazırlıklar devam ediyor

---

## 2. File Parsing: Mevcut Durum ve Geliştirme İhtiyacı
- PDF ve TXT dosya tipleri için otomatik parsing mevcut, DOCX desteği eklenmeli.

---

## 3. Model Bazlı Vector Query ve Doküman-Model İlişkisi
- Dokümanlar ile modeller arasında doğrudan ilişki yok.
- Milvus'ta embedding'ler model ile ilişkilendirilmiyor, model bazlı arama yapılamıyor.
- Geliştirme: Doküman-model ilişki tablosu, embedding metadata'sında model_id, endpointlerde model_id filtresi eklenmeli.

---

## 4. Amaç ve Katkı
- File parsing ile yüklenen her dosyanın içeriği otomatik işlenir, arama ve embedding için hazır hale gelir.
- Model bazlı vector query ile her modelin kendi bilgi havuzu olur, veri izolasyonu ve özelleştirme sağlanır.
- Otomatik test altyapısı ile servisler arası entegrasyon ve güvenilirlik artırıldı.

---

## 5. Referanslar
- src/backend/main.py
- src/backend/routers/embedding.py
- src/backend/services/file/service.py
- src/backend/services/embedding_service.py
- src/backend/services/milvus_service.py
- src/backend/services/model.py
- src/backend/services/rag_service.py 