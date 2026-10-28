from dotenv import load_dotenv
from langfuse import get_client
from langfuse.langchain import CallbackHandler
import os

load_dotenv()  # read keys from .env before Langfuse starts


def get_handler() -> CallbackHandler:
    """New wire for each request."""
    return CallbackHandler()


def langfuse_status() -> str:
    """Honest, short check: never leaks error details."""
    if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
        return "missing keys"
    try:
        return "ok" if get_client().auth_check() else "invalid keys"
    except Exception as e:
        return f"error: {type(e).__name__}"