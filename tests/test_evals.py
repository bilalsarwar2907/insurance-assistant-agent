import json
import uuid
from pathlib import Path
from app import rag
import os

import pytest

from app.graph import graph

CASES = json.loads((Path(__file__).parent.parent / "evals" / "cases.json").read_text(encoding="utf-8"))


def run(message: str) -> dict:
    """Send one message in a fresh session and return the final state."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    return graph.invoke({"message": message}, config)


class TestPolicyLookup:
    @pytest.mark.parametrize("case", CASES["policy"], ids=lambda c: c["message"])
    def test_case(self, case):
        result = run(case["message"])
        assert result["status"] == case["expected_status"]
        assert result["route"] == case["expected_route"]

class TestClaimLookup:
    @pytest.mark.parametrize("case", CASES["claim"], ids=lambda c: c["message"])
    def test_case(self, case):
        result = run(case["message"])
        assert result["status"] == case["expected_status"]
        assert result["route"] == case["expected_route"]        

class TestRag:
    """CI layer: if search finds file X, the reply must cite X (citation logic, not search quality)."""

    @pytest.mark.parametrize("case", CASES["rag"], ids=lambda c: c["expected_source"])
    def test_cites_found_source(self, case, monkeypatch):
        src = case["expected_source"]
        monkeypatch.setattr(rag, "search_policies", lambda q: {"source": src, "text": "policy text", "score": 0.9})
        monkeypatch.setattr(rag, "is_relevant", lambda q, t: True)
        monkeypatch.setattr(rag, "write_answer", lambda q, t: "Short answer.")

        result = run(case["message"])

        assert result["status"] == "answered"
        assert result["sources"] == [src]
        assert f"[Source: {src}]" in result["reply"]

REAL_SEARCH = rag.search_policies   # grabbed at import time, before conftest fakes it


@pytest.mark.skipif(not os.getenv("RUN_REAL_EVALS"), reason="set RUN_REAL_EVALS=1 to run real Gemini + Qdrant")
class TestRagReal:
    """Real layer: real embeddings + Qdrant must find the expected file."""

    @pytest.mark.parametrize("case", CASES["rag"], ids=lambda c: c["expected_source"])
    def test_finds_expected_source(self, case):
        found = REAL_SEARCH(case["message"])
        assert found["source"] == case["expected_source"]
        assert found["score"] >= rag.THRESHOLD        