import pytest
from app import rag

FAKE_DOC = {"source": "cancellation.txt", "text": "You can cancel with 30 days notice.", "score": 0.9}


@pytest.fixture(autouse=True)
def fake_rag(monkeypatch):
    monkeypatch.setattr(rag, "search_policies", lambda q: FAKE_DOC)
    monkeypatch.setattr(rag, "is_relevant", lambda q, t: "cancel" in q.lower())