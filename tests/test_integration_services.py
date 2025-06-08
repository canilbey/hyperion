import pytest
import os
import time
import psycopg2
import redis
import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("POSTGRES_USER", "hyperion")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "hyperion123")
DB_NAME = os.getenv("POSTGRES_DB", "hyperion_test")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


def test_backend_healthcheck():
    # Backend health endpoint'i kontrol et
    url = f"{BACKEND_URL}/api/health"
    for _ in range(10):
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(2)
    pytest.fail("Backend health endpoint'e ulaşılamadı!")

def test_postgres_connection():
    # Postgres'e bağlanabiliyor mu?
    for _ in range(10):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                dbname=DB_NAME,
                connect_timeout=2
            )
            conn.close()
            return
        except Exception:
            time.sleep(2)
    pytest.fail("PostgreSQL bağlantısı başarısız!")

def test_redis_connection():
    # Redis'e bağlanabiliyor mu?
    for _ in range(10):
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, socket_connect_timeout=2)
            pong = r.ping()
            if pong:
                return
        except Exception:
            time.sleep(2)
    pytest.fail("Redis bağlantısı başarısız!") 