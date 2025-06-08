import os
import requests

def get_api_key():
    return os.getenv("API_KEY")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_KEY = get_api_key()

headers = {"Authorization": f"Bearer {API_KEY}"}

def test_model_create_with_api_key():
    url = f"{BACKEND_URL}/model/create"
    data = {
        "model_name": "test_model_api_key",
        "model": "test",
        "system_prompt": "test"
    }
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == 200, f"Status: {r.status_code}, Body: {r.text}"
    assert "model_id" in r.json()

def test_document_upload():
    url = f"{BACKEND_URL}/document/upload"
    file_path = "tests/test_document.pdf"
    with open(file_path, "rb") as f:
        files = {"file": ("test_document.pdf", f, "application/pdf")}
        r = requests.post(url, files=files, headers=headers)
    assert r.status_code in (200, 201), f"Status: {r.status_code}, Body: {r.text}"
    # Yükleme sonrası dönen cevabın beklenen alanları içerdiğini kontrol et
    assert "document_id" in r.json() or "success" in r.json() or r.text.lower().find("ok") != -1 