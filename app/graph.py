import re
from app import rag
from app.tools import get_policy, claim_status
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
import operator
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import InMemorySaver




class AgentState(TypedDict, total=False):
    message: str       # customer's text
    route: str         # chosen path: "policy", "claim", "handover"...
    tool_result: dict  # data from get_policy / claim_status
    reply: str         # answer to send back
    status: str        # e.g. "answered" or "handover"
    history: Annotated[list[str], operator.add]   # add, don't replace
    sources: list[str]   # policy files used for the answer

def router(state: AgentState) -> dict:
    message = state["message"]
    if "CLM-" in message:
        return {"route": "claim"}
    if "POL-" in message:
        return {"route": "policy"}
    return {"route": "rag"}  # default to RAG (retrieval-augmented generation)

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

HANDOVER_REPLY = "I can't answer that reliably. I'll connect you with a colleague."


def handover_node(state: AgentState) -> dict:
    return {"reply": HANDOVER_REPLY, "status": "handover"}

BLOCKED = ["password", "hack", "other customer"]
FALLBACK_REPLY = "Sorry, I can't help with that request."


def guardrail(state: AgentState) -> dict:
    text = state["message"].lower()
    route = "blocked" if any(word in text for word in BLOCKED) else "ok"
    return {"route": route, "history": [state["message"]], "sources": []}


def fallback_node(state: AgentState) -> dict:
    return {"reply": FALLBACK_REPLY, "status": "blocked"}

# Turns tool data into a reply
def respond_node(state: AgentState) -> dict:
    return {"reply": f"Here is what I found: {state['tool_result']}", "status": "answered"}


# Signposts (conditional edges)
def after_guardrail(state: AgentState) -> str:
    return "fallback" if state.get("route") == "blocked" else "router"


def after_router(state: AgentState) -> str:
    return state["route"]          # "claim", "policy" or "handover"


def after_tool(state: AgentState) -> str:
    return "handover" if state["route"] == "handover" else "respond"

def rag_node(state: AgentState) -> dict:
    question = state["message"]
    found = rag.search_policies(question)
    if found["score"] < rag.THRESHOLD or not rag.is_relevant(question, found["text"]):
        return {"route": "handover"}
    answer = rag.write_answer(question, found["text"])
    if "NOT IN TEXT" in answer:
        return {"route": "handover"}
    return {
        "reply": f"{answer} [Source: {found['source']}]",
        "status": "answered",
        "sources": [found["source"]],
    }


def after_rag(state: AgentState) -> str:
    return "handover" if state["route"] == "handover" else END


# Build the graph
builder = StateGraph(AgentState)
builder.add_node("guardrail", guardrail)
builder.add_node("router", router)
builder.add_node("claim", claim_node)
builder.add_node("policy", policy_node)
builder.add_node("respond", respond_node)
builder.add_node("handover", handover_node)
builder.add_node("fallback", fallback_node)
builder.add_node("rag", rag_node)
builder.add_conditional_edges("rag", after_rag)

builder.add_edge(START, "guardrail")
builder.add_conditional_edges("guardrail", after_guardrail)
builder.add_conditional_edges("router", after_router)
builder.add_conditional_edges("claim", after_tool)
builder.add_conditional_edges("policy", after_tool)
builder.add_edge("respond", END)
builder.add_edge("handover", END)
builder.add_edge("fallback", END)

graph = builder.compile(checkpointer=InMemorySaver())