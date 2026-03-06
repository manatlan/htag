import threading
import contextvars
from typing import Any


class _HtagLocal(threading.local):
    stack: list["GTag"]
    current_eval: "GTag | None"  # Track which GTag is evaluating a reactive lambda

    def __init__(self) -> None:
        super().__init__()
        self.stack = []
        self.current_eval = None


_ctx = _HtagLocal()

from starlette.requests import Request
from starlette.websockets import WebSocket

# Global context for passing the current request/websocket object
current_request: contextvars.ContextVar[Request | WebSocket | None] = contextvars.ContextVar(
    "current_request", default=None
)
