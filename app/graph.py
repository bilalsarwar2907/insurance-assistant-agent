import re
from app.tools import get_policy, claim_status
from typing import TypedDict


class AgentState(TypedDict, total=False):
    message: str       # customer's text
    route: str         # chosen path: "policy", "claim", "handover"...
    tool_result: dict  # data from get_policy / claim_status
    reply: str         # answer to send back
    status: str        # e.g. "answered" or "handover"

def router(state: AgentState) -> dict:
    message = state["message"]
    if "CLM-" in message:
        return {"route": "claim"}
    if "POL-" in message:
        return {"route": "policy"}
    return {"route": "handover"}    

def claim_node(state: AgentState) -> dict:
    match = re.search(r"CLM-\d+", state["message"])
    result = claim_status(match.group())
    if result is None:
        return {"route": "handover"}
    return {"tool_result": result}


def policy_node(state: AgentState) -> dict:
    match = re.search(r"POL-\d+", state["message"])
    result = get_policy(match.group())
    if result is None:
        return {"route": "handover"}
    return {"tool_result": result}