# Hyperion API Dokümantasyonu

Bu doküman, Hyperion platformunun REST API uç noktalarını, giriş/çıkış yapıları ve örneklerle birlikte açıklamaktadır. Her endpoint için Swagger/OpenAPI açıklama önerileri de eklenmiştir.

---

## Kimlik Doğrulama ve Kullanıcı Yönetimi

### 1. Kayıt Ol (Signup)
- **Endpoint:** `POST /api/auth/signup`
- **Açıklama:** Yeni kullanıcı kaydı oluşturur.
- **Swagger Açıklaması:**
  - summary: Kullanıcı kaydı
  - description: Yeni bir kullanıcı oluşturur. E-posta benzersiz olmalı, şifre politikası uygulanır.
  - requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
              password:
                type: string
                format: password
  - responses:
      200:
        description: Başarılı kayıt
      400:
        description: Geçersiz veri veya e-posta zaten kayıtlı
- **Girdi:**
  ```json
  {
    "email": "kullanici@ornek.com",
    "password": "gizliSifre"
  }
  ```
- **Çıktı:** Başarılıysa kullanıcı bilgisi veya oturum tokeni.
- **Örnek cURL:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/signup \
    -H "Content-Type: application/json" \
    -d '{"email":"kullanici@ornek.com","password":"gizliSifre"}'
  ```

---

### 2. Giriş Yap (Login)
- **Endpoint:** `POST /api/auth/login`
- **Açıklama:** Kullanıcıyı doğrular ve JWT token döner.
- **Swagger Açıklaması:**
  - summary: Kullanıcı girişi
  - description: Kullanıcıyı doğrular ve JWT token döner. Token, korumalı endpointlerde kullanılmalıdır.
  - requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              email:
                type: string
                format: email
              password:
                type: string
                format: password
  - responses:
      200:
        description: Başarılı giriş ve JWT token
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                expires_in:
                  type: integer
      401:
        description: Geçersiz kimlik bilgisi
- **Girdi:**
  ```json
  {
    "email": "kullanici@ornek.com",
    "password": "gizliSifre"
  }
  ```
- **Çıktı:**
  ```json
  {
    "access_token": "jwt_token",
    "expires_in": 1800
  }
  ```
- **Örnek cURL:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"kullanici@ornek.com","password":"gizliSifre"}'
  ```

---

### 3. Şifre Sıfırlama
- **Endpoint:** `POST /api/auth/request-password-reset`
  - **Açıklama:** Şifre sıfırlama bağlantısı gönderir.
  - **Swagger Açıklaması:**
    - summary: Şifre sıfırlama isteği
    - description: Kullanıcıya şifre sıfırlama bağlantısı gönderir.
    - requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
    - responses:
        200:
          description: E-posta gönderildi
        404:
          description: Kullanıcı bulunamadı
  - **Girdi:** `{ "email": "kullanici@ornek.com" }`

- **Endpoint:** `POST /api/auth/reset-password`
  - **Açıklama:** Şifreyi sıfırlar.
  - **Swagger Açıklaması:**
    - summary: Şifre sıfırla
    - description: Geçerli token ile yeni şifre belirler.
    - requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                new_password:
                  type: string
                  format: password
    - responses:
        200:
          description: Şifre başarıyla değiştirildi
        400:
          description: Geçersiz token veya şifre
  - **Girdi:** `{ "token": "reset_token", "new_password": "yeniSifre" }`

---

### 4. Çıkış Yap (Logout)
- **Endpoint:** `POST /api/auth/logout`
- **Açıklama:** Oturumu sonlandırır.
- **Swagger Açıklaması:**
  - summary: Çıkış yap
  - description: Kullanıcı oturumunu sonlandırır. Token gereklidir.
  - responses:
      200:
        description: Başarılı çıkış
      401:
        description: Geçersiz veya eksik token
- **Girdi:** (Token ile çağrılır)
- **Çıktı:** Başarı/başarısızlık mesajı.

---

## Sağlık ve Gözlemlenebilirlik

### 5. Sağlık Kontrolü
- **Endpoint:** `GET /health` veya `GET /api/health`
- **Açıklama:** Servisin çalışıp çalışmadığını kontrol eder.
- **Swagger Açıklaması:**
  - summary: Sağlık kontrolü
  - description: Servisin ve bağlı servislerin durumunu döner.
  - responses:
      200:
        description: Servis sağlıklı
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
- **Çıktı:**
  ```json
  {
    "status": "ok"
  }
  ```

---

## Dosya Yükleme

### 6. Dosya Yükle
- **Endpoint:** `POST /upload`
- **Açıklama:** Dosya yükler, işler ve vektörleştirir.
- **Swagger Açıklaması:**
  - summary: Dosya yükle
  - description: Dosya yükler ve işlenmek üzere sisteme kaydeder.
  - requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            properties:
              file:
                type: string
                format: binary
  - responses:
      200:
        description: Dosya başarıyla yüklendi
      400:
        description: Geçersiz dosya
- **Girdi:** Form-data ile dosya (`file`)
- **Çıktı:** Yüklenen dosyanın bilgisi ve işlenme sonucu.
- **Örnek cURL:**
  ```bash
  curl -X POST http://localhost:8000/upload \
    -F "file=@/path/to/dosya.pdf"
  ```

---

## Sohbet (Chat) Yönetimi

### 7. Mesaj Gönder / Sohbet Başlat
- **Endpoint:** `POST /chat`
- **Açıklama:** Yeni sohbet başlatır veya mesaj gönderir.
- **Swagger Açıklaması:**
  - summary: Sohbet başlat veya mesaj gönder
  - description: Yeni bir sohbet başlatır veya mevcut sohbete mesaj ekler.
  - requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              message:
                type: string
  - responses:
      200:
        description: Sohbet cevabı
      401:
        description: Kimlik doğrulama gerekli
- **Girdi:**
  ```json
  {
    "message": "Merhaba!"
  }
  ```
- **Çıktı:** Sohbet cevabı.
- **Örnek cURL:**
  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"message":"Merhaba!"}'
  ```

---

### 8. Sohbetleri Listele
- **Endpoint:** `GET /chats`
- **Açıklama:** Kullanıcıya ait sohbetleri listeler.
- **Swagger Açıklaması:**
  - summary: Sohbetleri listele
  - description: Kullanıcıya ait tüm sohbetleri döner.
  - responses:
      200:
        description: Sohbet listesi
      401:
        description: Kimlik doğrulama gerekli
- **Çıktı:** Sohbet listesi.

### 9. Sohbet Geçmişi Getir
- **Endpoint:** `GET /chats/{identifier}/messages`
- **Açıklama:** Belirli bir sohbetin mesaj geçmişini getirir.
- **Swagger Açıklaması:**
  - summary: Sohbet geçmişi getir
  - description: Belirli bir sohbetin tüm mesajlarını döner.
  - parameters:
      - name: identifier
        in: path
        required: true
        schema:
          type: string
  - responses:
      200:
        description: Mesaj listesi
      404:
        description: Sohbet bulunamadı
- **Çıktı:** Mesajlar.

### 10. Sohbet Sil
- **Endpoint:** `DELETE /chats/{identifier}`
- **Açıklama:** Belirli bir sohbeti siler.
- **Swagger Açıklaması:**
  - summary: Sohbet sil
  - description: Belirli bir sohbeti siler.
  - parameters:
      - name: identifier
        in: path
        required: true
        schema:
          type: string
  - responses:
      200:
        description: Başarıyla silindi
      404:
        description: Sohbet bulunamadı
- **Çıktı:** Silme sonucu.

---

## Model Yönetimi

### 11. Model Oluştur
- **Endpoint:** `POST /model/create`
- **Açıklama:** Yeni bir model kaydı oluşturur.
- **Swagger Açıklaması:**
  - summary: Model oluştur
  - description: Yeni bir model kaydı oluşturur.
  - requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              model_name:
                type: string
              provider:
                type: string
              api_key:
                type: string
  - responses:
      200:
        description: Model başarıyla oluşturuldu
      400:
        description: Geçersiz veri
- **Girdi:** Model bilgileri (adı, sağlayıcı, API anahtarı vb.)
- **Çıktı:** Oluşturulan modelin bilgisi.

### 12. Modelleri Listele
- **Endpoint:** `GET /models`
- **Açıklama:** Tüm modelleri listeler.
- **Swagger Açıklaması:**
  - summary: Modelleri listele
  - description: Sistemdeki tüm modelleri döner.
  - responses:
      200:
        description: Model listesi
- **Çıktı:** Model listesi.

### 13. Model Bilgisi Getir
- **Endpoint:** `GET /model/{model_id}`
- **Açıklama:** Belirli bir modelin detaylarını getirir.
- **Swagger Açıklaması:**
  - summary: Model bilgisi getir
  - description: Belirli bir modelin detaylarını döner.
  - parameters:
      - name: model_id
        in: path
        required: true
        schema:
          type: string
  - responses:
      200:
        description: Model detayları
      404:
        description: Model bulunamadı
- **Çıktı:** Model detayları.

### 14. Model Sil
- **Endpoint:** `DELETE /model/{model_id}`
- **Açıklama:** Belirli bir modeli siler.
- **Swagger Açıklaması:**
  - summary: Model sil
  - description: Belirli bir modeli siler.
  - parameters:
      - name: model_id
        in: path
        required: true
        schema:
          type: string
  - responses:
      200:
        description: Başarıyla silindi
      404:
        description: Model bulunamadı
- **Çıktı:** Silme sonucu.

---

## Embedding Servisi

### 15. Embedding Modellerini Listele
- **Endpoint:** `GET /embedding/models`
- **Açıklama:** Kullanılabilir embedding modellerini listeler.
- **Swagger Açıklaması:**
  - summary: Embedding modellerini listele
  - description: Kullanılabilir embedding modellerini döner.
  - responses:
      200:
        description: Model listesi
- **Çıktı:** Model listesi.

### 16. Embedding Servis Sağlık Kontrolü
- **Endpoint:** `GET /embedding/health`
- **Açıklama:** Embedding servisinin durumunu kontrol eder.
- **Swagger Açıklaması:**
  - summary: Embedding servis sağlık kontrolü
  - description: Embedding servisinin ve modelinin durumunu döner.
  - responses:
      200:
        description: Servis sağlıklı
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: ok
                model:
                  type: string
- **Çıktı:**
  ```json
  {
    "status": "ok",
    "model": "kullanilan_model"
  }
  ```

---

## Genel Notlar
- Tüm korumalı endpointler JWT ile kimlik doğrulama gerektirir.
- API, OpenAPI/Swagger ile otomatik olarak dokümante edilmiştir.
- Yanıtlar JSON formatındadır.
- Hatalar HTTP hata kodları ve açıklayıcı mesajlarla döner. 