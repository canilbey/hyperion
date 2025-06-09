#!/usr/bin/env python3

import requests
import json
import time

# Test URL'leri
BASE_URL = "http://localhost:8000"
UPLOAD_URL = f"{BASE_URL}/upload"
CHAT_URL = f"{BASE_URL}/chat"
MODEL_CREATE_URL = f"{BASE_URL}/model/create"

def test_rag_integration():
    """RAG entegrasyonunu test eder"""
    
    print("🚀 RAG entegrasyonu test başlıyor...")
    
    # 1. Önce bir model oluştur
    print("\n1️⃣  Model oluşturuluyor...")
    model_data = {
        "provider": "openrouter",
        "model": "deepseek/deepseek-chat",
        "model_name": "DeepSeek Test",
        "system_prompt": "Sen yardımcı bir asistansın.",
        "api_key": "sk-or-v1-dummy-key-for-test",  # Test key
        "temperature": 0.7,
        "max_tokens": 1000,
        "is_active": True
    }
    
    try:
        response = requests.post(MODEL_CREATE_URL, json=model_data)
        if response.status_code == 200:
            model_result = response.json()
            model_id = model_result.get("model_id")
            print(f"✅ Model oluşturuldu: {model_id}")
        else:
            print(f"❌ Model oluşturulamadı: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Model oluşturma hatası: {e}")
        return False
    
    # 2. Test dosyası upload et
    print("\n2️⃣  Test dosyası upload ediliyor...")
    test_content = """
    Hyperion RAG Platformu
    
    Bu platform, kullanıcıların belgelerini yükleyip, bu belgeler hakkında sorular sorabileceği
    gelişmiş bir RAG (Retrieval-Augmented Generation) sistemidir.
    
    Ana özellikler:
    - PDF ve TXT dosya desteği
    - Otomatik embedding oluşturma
    - Vector database (Milvus) entegrasyonu
    - Chat tabanlı soru-cevap sistemi
    - Multiple LLM provider desteği
    
    Bu test dosyası RAG entegrasyonunu test etmek için oluşturulmuştur.
    """
    
    # Test dosyasını oluştur
    with open("/tmp/test-rag-doc.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open("/tmp/test-rag-doc.txt", "rb") as f:
            files = {"file": ("test-rag-doc.txt", f, "text/plain")}
            response = requests.post(UPLOAD_URL, files=files)
        
        if response.status_code == 200:
            upload_result = response.json()
            print(f"✅ Dosya upload edildi: {upload_result['file_id']}")
        else:
            print(f"❌ Dosya upload edilemedi: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Upload hatası: {e}")
        return False
    
    # 3. Embedding işleminin tamamlanmasını bekle
    print("\n3️⃣  Embedding işlemi tamamlanana kadar bekleniyor...")
    time.sleep(3)
    
    # 4. RAG entegrasyonlu chat testi
    print("\n4️⃣  RAG entegrasyonlu chat test ediliyor...")
    
    chat_data = {
        "messages": [
            {
                "role": "user",
                "content": "Hyperion platformunun ana özelliklerini açıklar mısın?"
            }
        ],
        "custom_config": {
            "model_id": model_id
        }
    }
    
    try:
        response = requests.post(CHAT_URL, json=chat_data)
        if response.status_code == 200:
            chat_result = response.json()
            print(f"✅ Chat yanıtı alındı:")
            print(f"📝 Yanıt: {chat_result['message']['content']}")
            print(f"🤖 Model: {chat_result['model_used']}")
            
            # RAG context'in kullanılıp kullanılmadığını kontrol et
            if "hyperion" in chat_result['message']['content'].lower() or \
               "rag" in chat_result['message']['content'].lower() or \
               "embedding" in chat_result['message']['content'].lower():
                print("🎉 RAG entegrasyonu BAŞARILI! Yanıtta belgeden bilgi kullanıldı.")
                return True
            else:
                print("⚠️  RAG entegrasyonu belirsiz. Belge bilgisi tespit edilemedi.")
                return False
        else:
            print(f"❌ Chat hatası: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat test hatası: {e}")
        return False

if __name__ == "__main__":
    # Backend'in hazır olmasını bekle
    print("⏳ Backend'in hazır olması bekleniyor...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Backend hazır!")
                break
        except:
            pass
        time.sleep(2)
        print(f"   Deneme {i+1}/10...")
    else:
        print("❌ Backend hazır değil, test iptal ediliyor.")
        exit(1)
    
    # Test çalıştır
    success = test_rag_integration()
    
    if success:
        print("\n🎉 RAG entegrasyonu test başarıyla tamamlandı!")
    else:
        print("\n❌ RAG entegrasyonu test başarısız!")
    
    exit(0 if success else 1) 