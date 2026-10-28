import json
import uuid
from pathlib import Path

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