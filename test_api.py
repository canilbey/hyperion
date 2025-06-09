import pytest
from fastapi.testclient import TestClient
from backend.main import app
from uuid import uuid4

client = TestClient(app)

def test_model_management():
    # Test model creation
    create_res = client.post("/model/create", json={
        "model_name": "test_model",
        "model": "test",
        "system_prompt": "test"
    })
    assert create_res.status_code == 200
    model_id = create_res.json()["model_id"]

    # Test model listing
    list_res = client.get("/model")
    assert list_res.status_code == 200
    assert any(m["model_id"] == model_id for m in list_res.json())

    # Test model retrieval
    get_res = client.get(f"/model/{model_id}")
    assert get_res.status_code == 200
    assert get_res.json()["model_id"] == model_id

    # Test model update
    update_res = client.patch(f"/model/{model_id}", json={"system_prompt": "updated"})
    assert update_res.status_code == 200
    assert update_res.json()["system_prompt"] == "updated"

    # Test model deletion
    del_res = client.delete(f"/model/{model_id}")
    assert del_res.status_code == 200

def test_chat_management():
    # Test chat creation
    chat_res = client.post("/chat/test_chat", json={
        "message": [{"role": "user", "content": "hello"}],
        "chat_name": "test_chat"
    })
    assert chat_res.status_code == 200
    chat_id = chat_res.json()["chat_id"]

    # Test chat listing
    list_res = client.get("/chat")
    assert list_res.status_code == 200
    assert any(c["chat_id"] == chat_id for c in list_res.json())

    # Test chat update
    update_res = client.patch(f"/chat/{chat_id}", json={"label": "updated"})
    assert update_res.status_code == 200

    # Test chat deletion
    del_res = client.delete(f"/chat/{chat_id}")
    assert del_res.status_code == 200