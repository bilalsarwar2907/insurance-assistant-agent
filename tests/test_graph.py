from app.graph import graph, HANDOVER_REPLY, FALLBACK_REPLY
import uuid


def run(message):
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}   # fresh session each test
    return graph.invoke({"message": message}, config)


def test_same_session_remembers():
    c = {"configurable": {"thread_id": "A"}}
    graph.invoke({"message": "hi"}, c)
    result = graph.invoke({"message": "CLM-002"}, c)
    assert result["history"] == ["hi", "CLM-002"]


def test_other_session_is_empty():
    graph.invoke({"message": "hi"}, {"configurable": {"thread_id": "X"}})
    result = graph.invoke({"message": "CLM-002"}, {"configurable": {"thread_id": "Y"}})
    assert result["history"] == ["CLM-002"]


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