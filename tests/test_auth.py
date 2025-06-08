import pytest
from fastapi.testclient import TestClient
from backend.main import app
from uuid import uuid4

client = TestClient(app)

TEST_EMAIL = f"testuser_{uuid4()}@example.com"
TEST_PASSWORD = "TestPassword123!"


def test_signup_success():
    res = client.post("/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == TEST_EMAIL
    assert "id" in data
    assert "roles" in data

def test_signup_duplicate():
    # İlk kayıt
    client.post("/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    # Aynı email ile tekrar kayıt
    res = client.post("/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]

def test_login_success():
    # Önce kullanıcıyı kaydet
    client.post("/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    # Doğru bilgilerle giriş
    res = client.post("/api/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["expires_in"] > 0

def test_login_wrong_password():
    # Önce kullanıcıyı kaydet
    client.post("/api/auth/signup", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    # Yanlış şifre ile giriş
    res = client.post("/api/auth/login", json={"email": TEST_EMAIL, "password": "WrongPassword!"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials" 