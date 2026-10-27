# Fictional test data (fixtures)
POLICIES = {
    "POL-001": {"type": "home", "holder": "Anna Jensen", "status": "active"},
    "POL-002": {"type": "travel", "holder": "Lars Nielsen", "status": "active"},
}

CLAIMS = {
    "CLM-001": {"policy_id": "POL-001", "status": "in review"},
    "CLM-002": {"policy_id": "POL-002", "status": "approved"},
}


def get_policy(policy_id: str):
    return POLICIES.get(policy_id)   # unknown ID -> None


def claim_status(claim_id: str):
    return CLAIMS.get(claim_id)      # unknown ID -> None