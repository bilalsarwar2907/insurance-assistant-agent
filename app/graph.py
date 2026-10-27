from typing import TypedDict


class AgentState(TypedDict, total=False):
    message: str       # customer's text
    route: str         # chosen path: "policy", "claim", "handover"...
    tool_result: dict  # data from get_policy / claim_status
    reply: str         # answer to send back
    status: str        # e.g. "answered" or "handover"