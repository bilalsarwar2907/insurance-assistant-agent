from app.tools import get_policy, claim_status


def test_known_policy():
    assert get_policy("POL-001")["holder"] == "Anna Jensen"


def test_unknown_policy():
    assert get_policy("POL-999") is None


def test_known_claim():
    assert claim_status("CLM-002")["status"] == "approved"


def test_unknown_claim():
    assert claim_status("CLM-999") is None

def test_claim_policy_link():
    claim = claim_status("CLM-001")
    policy = get_policy(claim["policy_id"])
    assert policy["holder"] == "Anna Jensen"    