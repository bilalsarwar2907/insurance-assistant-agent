from dotenv import load_dotenv
from langfuse import get_client
from langfuse.langchain import CallbackHandler

load_dotenv()  # read keys from .env before Langfuse starts


def get_handler() -> CallbackHandler:
    """New wire for each request."""
    return CallbackHandler()


def langfuse_status() -> str:
    """Honest check: are keys present and accepted?"""
    try:
        return "ok" if get_client().auth_check() else "missing keys"
    except Exception as e:
        return f"error: {e}"