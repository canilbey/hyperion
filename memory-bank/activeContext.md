# Active Context

## Şu Anki Odak
- File parsing pipeline'ına yeni dosya tipleri (DOCX vb.) eklenmesi
- Doküman-model ilişkisinin veri modeline eklenmesi ve model bazlı vector query desteği
- Milvus, PostgreSQL ve Redis entegrasyonlarının sürdürülebilirliği
- Servisler arası iletişim için otomatik test altyapısının güçlendirilmesi (pytest, docker-compose.test.yml)
- Build ve test süreçlerinin hızlandırılması, gereksiz build işlemlerinin önlenmesi
- Bağımlılık yönetimi ve test runner imajında eksik kütüphanelerin (ör. psycopg2) eklenmesi

## Son Yapılanlar
- Test runner ve izole test ortamı (docker-compose.test.yml) kuruldu
- API key ile korunan endpointler ve dosya yükleme endpointi için otomatik testler eklendi
- Test runner imajına psycopg2 eklendi, import hataları giderildi
- Kodda global async başlatma kaldırıldı, event loop hatası çözüldü
- Build süresi optimize edildi, gereksiz build işlemleri önlendi
- Tüm test ortamı container ve volume'leri temizlenerek sıfırdan build alındı
- PostgreSQL test veritabanı otomatik oluşturulacak şekilde ayarlandı

## Sonraki Adımlar
- File parsing pipeline'ına yeni dosya tipleri (DOCX vb.) eklenmeli
- Doküman-model ilişki tablosu ve model_id ile embedding ekleme/query desteği geliştirilmeli
- Milvus ve etcd bağlantı stabilitesi izlenecek
- Servisler arası iletişim ve veri akışı manuel/otomatik testlerle doğrulanacak
- Test runner ve build süreçleri için CI/CD entegrasyonu güçlendirilecek
- Gerekirse docker-compose ve migration süreçlerinde ek iyileştirme yapılacak 