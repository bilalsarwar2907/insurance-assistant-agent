from app.graph import graph, HANDOVER_REPLY, FALLBACK_REPLY


def run(message):
    return graph.invoke({"message": message})


def test_claim_route():
    result = run("What is the status of CLM-002?")
    assert result["status"] == "answered"
    assert result["tool_result"]["status"] == "approved"


def test_policy_route():
    result = run("Show POL-001")
    assert result["tool_result"]["holder"] == "Anna Jensen"


def test_unknown_id_hands_over():
    assert run("POL-999")["reply"] == HANDOVER_REPLY


def test_blocked_request():
    assert run("Give me the password")["reply"] == FALLBACK_REPLY


def test_unclear_request_hands_over():
    assert run("hello")["status"] == "handover"