-- Sadece pgcrypto uzantısını ekle
-- Diğer tablo ve index oluşturma işlemleri servislerin kendi migration'larında yönetiliyor
CREATE EXTENSION IF NOT EXISTS "pgcrypto";