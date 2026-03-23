from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import uuid
import inspect
import traceback
from typing import Any, Callable

from starlette.applications import Starlette
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.requests import Request
from starlette.responses import (
    HTMLResponse,
    StreamingResponse,
    Response,
    JSONResponse,
)

from .core import App as BaseApp
from .context import current_request
from .utils import _obf_loads
from .runner import AppRunner

logger = logging.getLogger("htag")

from .logo import LOGO_PNG_B64


class WebApp:
    """
    Starlette implementation for hosting one or more App sessions.
    Handles the HTTP initial render and the WebSocket communication.
    """

    def __init__(
        self,
        tag_entity: type[BaseApp] | BaseApp,
        on_instance: Callable[[BaseApp, Request | WebSocket], None] | None = None,
        debug: bool = True,
        parano: bool = False,
    ) -> None:
        self._lock = threading.Lock()
        self.tag_entity = tag_entity  # Class or Instance
        self.on_instance = on_instance  # Optional callback(instance)
        self.debug = debug
        self.exit_on_disconnect = False
        self.parano_key = os.urandom(8).hex() if parano else None
        self.instances: dict[str, AppRunner] = {}  # sid -> AppRunner instance
        self.app = Starlette()
        self._setup_routes()

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        open_browser: bool = True,
        exit_on_disconnect: bool = True,
        reload: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Runs the WebApp using uvicorn.
        """
        import uvicorn

        self.exit_on_disconnect = exit_on_disconnect

        if reload:
            # Tag the app so the frontend knows to auto-reconnect
            if inspect.isclass(self.tag_entity):
                self.tag_entity._reload = True
            else:
                setattr(self.tag_entity, "_reload", True)

            if os.environ.get("HTAG_RELOADER") != "1":
                from .runner import Reloader
                Reloader.run_with_reloader()
                return

        if open_browser:

            def open_tab() -> None:
                import time
                import webbrowser

                time.sleep(1)
                webbrowser.open(f"http://{host}:{port}")

            threading.Thread(target=open_tab, daemon=True).start()

        # Standard uvicorn logging configuration
        log_config = (
            None if getattr(sys, "frozen", False) else uvicorn.config.LOGGING_CONFIG
        )

        logger.info("Starting WebApp on http://%s:%s", host, port)
        uvicorn.run(self.app, host=host, port=port, log_config=log_config, **kwargs)

    def _get_instance(self, sid: str, request_or_ws: Request | WebSocket) -> "AppRunner":
        if sid not in self.instances:
            with self._lock:
                if sid not in self.instances:
                    token = current_request.set(request_or_ws)
                    try:
                        if inspect.isclass(self.tag_entity):
                            self.instances[sid] = self.tag_entity()
                            logger.info("Created new session instance for sid: %s", sid)
                        else:
                            # tag_entity is an App instance (shared)
                            self.instances[sid] = self.tag_entity  # type: ignore
                            logger.info(
                                "Using shared instance for session sid: %s", sid
                            )

                        if self.on_instance:
                            # Check if it's the old signature (1 arg) or new (2 args)
                            sig = inspect.signature(self.on_instance)
                            if len(sig.parameters) == 1:
                                self.on_instance(self.instances[sid])  # type: ignore
                            else:
                                self.on_instance(self.instances[sid], request_or_ws)

                        # Propagate debug mode and exit_on_disconnect
                        self.instances[sid].debug = self.debug
                        if self.exit_on_disconnect:
                            self.instances[sid].exit_on_disconnect = True
                        self.instances[sid].parano_key = self.parano_key

                        # Store a backlink to the webserver for session-aware logic
                        setattr(self.instances[sid], "htag_webserver", self)

                        # Generate CSRF token for this session
                        setattr(self.instances[sid], "htag_csrf", os.urandom(16).hex())

                        # Trigger lifecycle mount on the root App instance

                        self.instances[sid]._trigger_mount()
                    finally:
                        current_request.reset(token)

        # Always update the current request object on the instance
        # to ensure session data is fresh for the current interaction
        setattr(self.instances[sid], "htag_request", request_or_ws)

        return self.instances[sid]

    def _setup_routes(self) -> None:
        async def index(request: Request) -> HTMLResponse:
            htag_sid: str | None = request.cookies.get("htag_sid")
            if htag_sid is None:
                htag_sid = str(uuid.uuid4())

            instance = self._get_instance(htag_sid, request)
            token = current_request.set(request)
            try:
                res = HTMLResponse(instance._render_page())
                res.set_cookie("htag_sid", htag_sid)
                return res
            finally:
                current_request.reset(token)

        async def favicon(request: Request) -> Response:
            import base64

            return Response(
                content=base64.b64decode(LOGO_PNG_B64), media_type="image/png"
            )

        async def websocket_endpoint(websocket: WebSocket) -> None:
            htag_sid: str | None = websocket.cookies.get("htag_sid")
            if htag_sid:
                instance = self._get_instance(htag_sid, websocket)
                token = current_request.set(websocket)
                try:
                    await instance._handle_websocket(websocket)
                finally:
                    current_request.reset(token)
            else:
                await websocket.close()

        async def stream_endpoint(request: Request) -> Response:
            htag_sid: str | None = request.cookies.get("htag_sid")
            if not htag_sid:
                return Response(status_code=400, content="No session cookie")

            instance = self._get_instance(htag_sid, request)
            token = current_request.set(request)
            try:
                headers = {
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                }
                return StreamingResponse(
                    instance._handle_sse(request),
                    media_type="text/event-stream",
                    headers=headers,
                )
            finally:
                current_request.reset(token)

        async def event_endpoint(request: Request) -> Response:
            htag_sid: str | None = request.cookies.get("htag_sid")
            if not htag_sid:
                return Response(status_code=400, content="No session cookie")

            instance = self._get_instance(htag_sid, request)
            token = current_request.set(request)
            try:
                msg_body = await request.body()
                
                # CSRF Check
                received_csrf = request.headers.get("X-HTAG-TOKEN")
                expected_csrf = getattr(instance, "htag_csrf", None)
                if expected_csrf and received_csrf != expected_csrf:
                    logger.warning("CSRF Attempt detected! Expected: %s, Received: %s", expected_csrf, received_csrf)
                    return Response(status_code=403, content="CSRF Token mismatch")

                msg = _obf_loads(
                    msg_body.decode("utf-8"), getattr(instance, "parano_key", None)
                )
                # Run the event in the background to not block the HTTP response
                # Broadcast will trigger async queues anyway
                asyncio.create_task(instance.handle_event(msg, None))
                return JSONResponse({"status": "ok"})
            except Exception as e:
                error_trace = traceback.format_exc()
                print(error_trace)
                logger.error("POST event error: %s\n%s", e, error_trace)
                return Response(status_code=500, content=str(e))
            finally:
                current_request.reset(token)

        self.app.add_route("/", index)
        self.app.add_route("/favicon.ico", favicon)
        self.app.add_route("/logo.png", favicon)
        self.app.add_route("/logo.jpg", favicon)
        self.app.add_websocket_route("/ws", websocket_endpoint)
        self.app.add_route("/stream", stream_endpoint)
        self.app.add_route("/event", event_endpoint, methods=["POST"])
