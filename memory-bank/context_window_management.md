# Hyperion - Chat Context Window ve RAG Yönetimi

## Şimdiye Kadar Yapılanlar

- Her yeni mesajda, sadece en son user mesajı için RAG context ekleniyor. Önceki mesajların RAG context'leri tekrar eklenmiyor.
- LLM'ye gönderilecek mesajların toplam token sayısı yaklaşık olarak kelime sayısının iki katı ile tahmin ediliyor.
- Modelin context window/token limiti aşılırsa, en eski mesajdan başlayarak mesajlar otomatik olarak siliniyor. Böylece prompt büyümesi ve context window taşması engelleniyor.

## Yol Haritası ve Planlanan Geliştirmeler

### 1. Daha Hassas Token Hesaplama
- OpenAI modelleri için tiktoken gibi gerçek tokenizer entegrasyonu.
- Diğer modeller için uygun tokenizer veya daha iyi bir tahmin algoritması.
- Token sayısı tahmini yerine, gerçek token sayısına göre truncate işlemi.

### 2. Eski Mesajların Otomatik Özetlenmesi
- Context window dolmaya yakınken, en eski mesajları silmek yerine otomatik olarak özetle (ör. LLM ile özetlet).
- Özetlenen mesajları ayrı bir "system" mesajı olarak context'e ekle.
- Kullanıcıya, "sohbetin bir kısmı özetlendi" şeklinde bilgi ver.

### 3. Kullanıcıya Context Window Uyarısı
- Token limiti yaklaşınca kullanıcıya uyarı mesajı göster.
- İsteğe bağlı olarak, kullanıcıya "eski mesajları sil/özetle" seçeneği sun.

### 4. RAG Context Yönetimi Geliştirmeleri
- Sadece son user mesajı değil, son N user mesajı için RAG context eklenmesi (N parametreli).
- RAG context'lerin de özetlenerek eklenmesi.
- RAG context'lerin token limitine katkısı ayrı izlenip, gerekirse sadece RAG context truncate edilmesi.

### 5. Gelişmiş Context Window Stratejileri
- Mesajları sadece "user-assistant" çiftleri olarak gruplandırıp, en eski çiftleri birlikte silmek.
- "Önemli" olarak işaretlenen mesajların asla silinmemesi.
- Farklı model context window'larına göre dinamik strateji.

### 6. Geliştirici ve Kullanıcı Dokümantasyonu
- Tüm context yönetimi stratejilerinin ve limitlerin dokümantasyonu.
- Kullanıcıya "sohbet geçmişi nasıl yönetiliyor?" başlıklı bir yardım/doküman sayfası.

---

**Önerilen Uygulama Sırası:**
1. Daha hassas token hesaplama (tiktoken veya benzeri).
2. Eski mesajların otomatik özetlenmesi.
3. Kullanıcıya context window uyarısı.
4. RAG context yönetimi geliştirmeleri.
5. Gelişmiş context window stratejileri.
6. Dokümantasyon. 