import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Hyperion API"}

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_invalid_file_upload(client):
    initial_errors = _parse_metric(client.get("/metrics").content, "http_requests_total", ["status", "4xx"])
    
    response = client.post("/api/upload", files={"invalid": ("test.txt", b"")})
    assert response.status_code == 422
    
    # Verify error metrics and logs
    metrics = client.get("/metrics").content
    assert _parse_metric(metrics, "http_requests_total", ["status", "4xx"]) == initial_errors + 1
    assert b'log_level="ERROR"' in metrics  # Verify error logs in metrics

def _parse_metric(metrics_data, metric_name, labels=[]):
    """Helper to parse Prometheus metrics"""
    decoded = metrics_data.decode('utf-8')
    for line in decoded.split('\\n'):
        if line.startswith(metric_name):
            parts = line.split()
            if all(label in line for label in labels):
                return float(parts[1])
    return 0