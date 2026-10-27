from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_chat_valid_request():
    response = client.post("/chat", json={"session_id": "s1", "message": "hello"})
    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert "status" in body
    assert "sources" in body


def test_chat_missing_message():
    response = client.post("/chat", json={"session_id": "s1"})
    assert response.status_code == 422

def test_chat_missing_session_id():
    response = client.post("/chat",json ={"message":"hello"})    

def test_chat_uses_agent():
    response = client.post("/chat", json={"session_id": "api-1", "message": "CLM-002"})
    assert response.json()["status"] == "answered"    