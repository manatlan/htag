from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import traceback
import inspect
from typing import Any, Callable

"""
This file must not import anything from starlette natively to remain framework-agnostic.
But we need to type hint WebSocket from starlette.websockets, so we only import it if TYPE_CHECKING
or we use Any. Since we expect Starlette's WebSocket, we will just import it.
"""
from starlette.websockets import WebSocket

from .core import GTag, App as BaseApp
from .tag import Tag
from .utils import _obf_dumps, _obf_loads
from .context import current_request
from .client_js import CLIENT_JS

logger = logging.getLogger("htag")


class Reloader:
    """
    Watches for .py file changes in the current directory and restarts the process.
    Used by ChromeApp and WebApp when reload=True.
    """

    @staticmethod
    def get_mtimes() -> dict[str, float]:
        import stat

        mtimes = {}
        for root, _, files in os.walk("."):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    try:
                        mtimes[path] = os.stat(path)[stat.ST_MTIME]
                    except OSError:
                        continue
        return mtimes

    @classmethod
    def run_with_reloader(cls) -> None:
        import signal
        import subprocess
        import sys
        import time

        env = os.environ.copy()
        env["HTAG_RELOADER"] = "1"
        cmd = [sys.executable] + sys.argv

        while True:
            logger.info("Starting htag worker process (RELOADER ACTIVE)...")
            process = subprocess.Popen(cmd, env=env)
            last_mtimes = cls.get_mtimes()

            try:
                while process.poll() is None:
                    time.sleep(0.5)
                    current_mtimes = cls.get_mtimes()
                    changed = False
                    for path, mtime in current_mtimes.items():
                        if path not in last_mtimes or mtime > last_mtimes[path]:
                            logger.warning(
                                "** Code changed (%s), restarting server... **",
                                path,
                            )
                            changed = True
                            break

                    if changed:
                        process.terminate()
                        try:
                            process.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            process.kill()
                        break
            except KeyboardInterrupt:
                if process.poll() is None:
                    process.terminate()
                break

            if process.returncode is not None and process.returncode not in (
                0,
                signal.SIGTERM,
                -signal.SIGTERM,
            ):
                # Only restart if it was a clean exit or a termination (which we triggered)
                # If it crashed with an error, we still want to watch and restart when code changes
                # but we add a small delay to avoid hammering the CPU if it's a permanent crash
                time.sleep(1)
            elif process.returncode == 0:
                break


class Event:
    """
    Simulates a DOM Event.
    Attributes are dynamically populated from the client message.
    """

    def __init__(self, target: GTag, msg: dict[str, Any]) -> None:
        self.target = target
        self.id: str = msg.get("id", "")
        self.name: str = msg.get("event", "")
        # The primary data payload (htag v2 pattern)
        self.value = msg.get("data")
        # Flat access to msg['data'] (e.g., e.value, e.x, etc.)
        data = self.value if isinstance(self.value, dict) else {}
        for k, v in data.items():
            setattr(self, k, v)

    def __getitem__(self, name: str) -> Any:
        val = getattr(self, "value", None)
        if isinstance(val, dict) and name in val:
            return val[name]
        return getattr(self, name, None)

    def __getattr__(self, name: str) -> Any:
        return None

    def __repr__(self) -> str:
        return f"Event({self.name} on {self.target.tag})"


class AppRunner(BaseApp):
    """
    The main application class for htag.
    Handles HTML rendering, event dispatching, and WebSocket communication.
    """

    statics: list[GTag] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__("body", *args, **kwargs)
        self.exit_on_disconnect: bool = False  # Default behavior for Web/API apps
        self.debug: bool = True  # Local debug mode default
        self.websockets: set[WebSocket] = set()
        self.sse_queues: set[asyncio.Queue] = set()  # Queues for active SSE connections
        self.sent_statics: set[str] = set()  # Track assets already in browser

    @property
    def app(self) -> Any:
        """Property for backward compatibility: returns a Starlette instance hosting this App."""
        if not hasattr(self, "_app_host"):
            from .web import WebApp
            self._app_host = WebApp(self)
        return self._app_host.app

    def _render_page(self) -> str:
        # 1. Render the initial body FIRST to populate __rendered_callables
        try:
            body_html = self.render_initial()
        except Exception as e:
            error_trace = traceback.format_exc()
            print(error_trace)
            logger.error("Error during initial render: %s\n%s", e, error_trace)
            if self.debug:
                safe_trace = error_trace.replace("`", "\\`").replace("$", "\\$")
                body_html = f"<body><htag-error show='true'></htag-error><script>document.body.appendChild(document.createElement('htag-error')).show('Initial Render Error', `{safe_trace}`);</script></body>"
            else:
                body_html = "<body><h1>Internal Server Error</h1></body>"

        # 2. Collect ALL statics from the whole tree
        self.sent_statics.clear()
        all_statics: list[str] = []
        try:
            title = self.collect_statics(self, all_statics) or self.__class__.__name__
        except Exception:
            title = self.__class__.__name__
        self.sent_statics.update(all_statics)
        statics_html = "".join(all_statics)

        # Force protocol via cookie if present
        protocol_patch = ""
        request = current_request.get()
        if request and hasattr(request, "cookies"):
            mode = request.cookies.get("htag_mode")
            if mode in ("http", "sse"):
                # Robust mock for WebSocket (and EventSource for http mode)
                mock_js = "class{constructor(){Object.assign(this,{readyState:3,close:()=>{},send:()=>{}});setTimeout(()=>this.onerror&&this.onerror(new Event('error')),0)}}; ['CONNECTING','OPEN','CLOSING','CLOSED'].forEach((name,i)=>{if(window.WebSocket)window.WebSocket[name]=i; if(window.EventSource)window.EventSource[name]=i;});"
                if mode == "http":
                    protocol_patch = f"window.WebSocket=window.EventSource={mock_js}"
                else:
                    protocol_patch = f"window.WebSocket={mock_js}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <title>{title}</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="icon" href="/logo.png">
                {f"<script>{protocol_patch}</script>" if protocol_patch else ""}
                <script>{CLIENT_JS}</script>
                <script>
                    window.HTAG_RELOAD = {"true" if getattr(self, "_reload", False) else "false"};
                    window.PARANO = {f'"{self.parano_key}"' if getattr(self, "parano_key", None) else "null"};
                    window.HTAG_CSRF = {f'"{self.htag_csrf}"' if getattr(self, "htag_csrf", None) else "null"};
                </script>

                {statics_html}
            </head>
            {body_html}
        </html>
        """
        return html_content

    def _build_initial_payload(self) -> str:
        updates = {self.id: self.render_initial()}
        js: list[str] = []
        self.collect_updates(self, {}, js)
        return _obf_dumps(
            {"action": "update", "updates": updates, "js": js},
            getattr(self, "parano_key", None),
        )

    async def _handle_sse(self, request: Any):
        queue: asyncio.Queue = asyncio.Queue()
        self.sse_queues.add(queue)
        logger.info("New SSE connection (Total clients: %d)", len(self.sse_queues))

        # Send initial state
        try:
            payload_str = self._build_initial_payload()
            # EventSource requires 'data: {payload}\n\n'
            yield f"data: {payload_str}\n\n"
            self._flush_pending_lifecycle_generators(None)
        except Exception as e:
            logger.error("Failed to send initial SSE state: %s", e)

        try:
            while True:
                # Wait for next broadcast payload or client disconnect
                message = await queue.get()
                yield f"data: {message}\n\n"
        except asyncio.CancelledError:  # Raised when client disconnects
            pass
        except Exception as e:
            logger.error("SSE stream error: %s", e)
        finally:
            self.sse_queues.discard(queue)
            logger.info("SSE disconnected (Total clients: %d)", len(self.sse_queues))
            asyncio.create_task(self._handle_disconnect())

    async def _handle_websocket(self, websocket: WebSocket) -> None:
        headers = [
            (b"cache-control", b"no-cache"),
            (b"connection", b"keep-alive"),
            (b"x-accel-buffering", b"no"),
        ]
        await websocket.accept(headers=headers)
        self.websockets.add(websocket)
        logger.info(
            "New WebSocket connection (Total WS clients: %d)", len(self.websockets)
        )

        # Send initial state on connection/reconnection
        try:
            payload_str = self._build_initial_payload()
            await websocket.send_text(payload_str)
            logger.debug("Sent initial state to client")
            self._flush_pending_lifecycle_generators(websocket)
        except Exception as e:
            logger.error("Failed to send initial state: %s", e)

        try:
            while True:
                data = await websocket.receive_text()
                msg = _obf_loads(data, getattr(self, "parano_key", None))
                await self.handle_event(msg, websocket)
        except Exception:
            pass
        finally:
            if websocket in self.websockets:
                self.websockets.discard(websocket)
            logger.info(
                "WebSocket disconnected (Total WS clients: %d)", len(self.websockets)
            )
            asyncio.create_task(self._handle_disconnect())

    async def _handle_disconnect(self) -> None:
        """Centralized disconnect handler to manage graceful shutdown across WS and SSE"""
        if self.websockets or self.sse_queues:
            logger.debug(
                "Disconnect handler called, but still active clients: WS=%d, SSE=%d",
                len(self.websockets),
                len(self.sse_queues),
            )
            return  # Still active clients (WS or SSE)

        # Exit when last browser window is closed, IF enabled
        if self.exit_on_disconnect:
            logger.info("Last client disconnected, checking for exit...")
            # Give it a small delay in case of F5 / Page Refresh
            await asyncio.sleep(0.5)

            # Check again if a client reconnects during the delay
            if self.websockets or self.sse_queues:
                logger.info("Client reconnected quickly, aborting exit (likely F5)")
                return

            # Session-aware exit: only exit if NO other session has active connections
            active_sessions = []
            if hasattr(self, "htag_webserver"):
                webserver = getattr(self, "htag_webserver")
                for sid, inst in webserver.instances.items():
                    # Ensure inst has websockets attribute (it should if it's a server.App)
                    if getattr(inst, "websockets", set()) or getattr(inst, "sse_queues", set()):
                        active_sessions.append(f"{sid} (WS:{len(getattr(inst, 'websockets', []))}, SSE:{len(getattr(inst, 'sse_queues', []))})")

            if not active_sessions:
                # No sessions have active connections anymore
                logger.info("Last client disconnected, no other active sessions: exiting...")
                if hasattr(self, "_browser_cleanup"):
                    self._browser_cleanup()
                os._exit(0)
            else:
                logger.info("Active sessions still exist: %s", ", ".join(active_sessions))
        else:
            logger.info("Last client disconnected (server stays alive)")

    def render_initial(self) -> str:
        # Initial render of the page (body)
        return self.render_tag(self)

    def _walk_tree(self, tag: GTag, visitor: Callable[[GTag], None]) -> None:
        """Generic tree walker: visits static children and rendered callables."""
        visitor(tag)
        for child in tag.childs:
            if isinstance(child, GTag):
                self._walk_tree(child, visitor)
        for tag_list in tag._get_rendered_callables().values():
            for t in tag_list:
                self._walk_tree(t, visitor)

    def collect_updates(
        self, tag: GTag, updates: dict[str, str], js_calls: list[str]
    ) -> None:
        """
        Recursively traverses the tag tree to find 'dirty' tags that need re-rendering.
        Also collects pending JavaScript calls from tags.
        """

        def visitor(t: GTag) -> None:
            with t._GTag__lock:
                if t.is_dirty:
                    updates[t.id] = self.render_tag(t)
                pending_js = t._consume_js_calls()
                if pending_js:
                    js_calls.extend(pending_js)

        self._walk_tree(tag, visitor)

    def collect_statics(self, tag: GTag, result: list[str]) -> str | None:
        """Recursively collects statics from the whole tag tree, returns the first title found."""
        seen_ids = set()
        seen_contents = set(result)
        found_title: list[str | None] = [None]

        def visitor(t: GTag) -> None:
            s_instance = getattr(t, "statics", [])
            s_class = getattr(t.__class__, "statics", [])

            # Avoid processing the exact same list twice (common case)
            lists = [s_class]
            if s_instance is not s_class:
                lists.append(s_instance)

            for s_list in lists:
                if not isinstance(s_list, (list, tuple)):
                    s_list = [s_list]
                for s in s_list:
                    if isinstance(s, GTag) and s.tag == "title":
                        # We extract text, and don't add to results (special head treatment)
                        found_title[0] = s.text
                        continue

                    sid = id(s)
                    if sid in seen_ids:
                        continue
                    seen_ids.add(sid)

                    s_str = str(s)
                    if s_str not in seen_contents:
                        seen_contents.add(s_str)
                        result.append(s_str)

        self._walk_tree(tag, visitor)
        return found_title[0]

    def _push_to_fallback(self, payload: str) -> None:
        if not hasattr(self, "_fallback_queue"):
            self._fallback_queue = []
        if len(self._fallback_queue) < 1000:
            self._fallback_queue.append(payload)


    async def handle_event(self, msg: dict[str, Any], ws: WebSocket | None) -> None:
        logger.info(f"handle_event {msg}")
        
        if msg.get("action") == "log_error":
            logger.error("Client JavaScript Error:\n%s", msg.get("error", "Unknown error"))
            return

        tag_id: str | None = msg.get("id")
        event_name: str | None = msg.get("event")

        if not isinstance(tag_id, str):
            return

        target_tag = self.find_tag(self, tag_id)
        if target_tag:
            data = msg.get("data", {})
            callback_id = data.get("callback_id") if isinstance(data, dict) else None
            # Auto-sync values from client (bypass __setattr__ to avoid re-rendering the input while typing)
            if isinstance(data, dict):
                for k in ["value", "checked", "name"]:
                    if k in data:
                        target_tag._set_attr_direct(k, data[k])

            if event_name in target_tag._get_events():
                logger.info(
                    "Event '%s' on tag %s (id: %s)",
                    event_name,
                    target_tag.tag,
                    target_tag.id,
                )
                callback = target_tag._get_events()[event_name]
                if isinstance(callback, str):
                    # Raw JS string event — no server-side dispatch needed
                    await self.broadcast_updates(result=None, callback_id=callback_id)
                    return
                event = Event(target_tag, msg)
                try:
                    if asyncio.iscoroutinefunction(callback):
                        res = await callback(event)
                    else:
                        res = callback(event)

                    # Handle generators/async generators for intermediate rendering
                    if inspect.isasyncgen(res):
                        async for _ in res:
                            await self.broadcast_updates()
                        res = None  # Async generators don't easily return a final value
                    elif inspect.isgenerator(res):
                        try:
                            while True:
                                next(res)
                                await self.broadcast_updates()
                        except StopIteration as e:
                            res = e.value  # This is the return value of the generator

                    # Sanitize result: we don't want to send GTag instances (not JSON serializable)
                    if isinstance(res, GTag):
                        res = True  # Convert to a simple truthy value

                    # Final broadcast after callback finishes, including the result if any
                    await self.broadcast_updates(result=res, callback_id=callback_id, ws=ws)
                except Exception as e:
                    error_trace: str = traceback.format_exc()
                    error_msg: str = (
                        f"Error in {event_name} callback: {str(e)}\n{error_trace}"
                    )
                    print(error_msg)
                    logger.error(error_msg)
                    # Use broadcast-like update for error reporting
                    err_payload: str = _obf_dumps(
                        {
                            "action": "error",
                            "traceback": error_trace
                            if self.debug
                            else "Internal Server Error",
                            "callback_id": callback_id,
                            "result": None,
                        },
                        getattr(self, "parano_key", None),
                    )

                    has_sent = False
                    if ws:
                        try:
                            await ws.send_text(err_payload)
                            has_sent = True
                        except Exception:
                            pass
                    else:
                        # Fallback Mode: Trigger error broadcast through SSE
                        for queue in self.sse_queues:
                            queue.put_nowait(err_payload)
                            has_sent = True

                    if not has_sent:
                        self._push_to_fallback(err_payload)

                    return
            else:
                await self.broadcast_updates(result=None, callback_id=callback_id, ws=ws)
        else:
            # tag not found (or missing tag_id)
            # if we have a callback_id, we MUST respond to resolve the client-side promise
            data = msg.get("data", {})
            callback_id = (
                data.get("callback_id") if isinstance(data, dict) else None
            )
            if callback_id:
                await self.broadcast_updates(result=None, callback_id=callback_id, ws=ws)

        self._flush_pending_lifecycle_generators(ws)

    def _flush_pending_lifecycle_generators(self, ws: WebSocket | None = None) -> None:
        if hasattr(self, "_pending_lifecycle_generators") and self._pending_lifecycle_generators:
            while self._pending_lifecycle_generators:
                tag, gen = self._pending_lifecycle_generators.pop(0)
                asyncio.create_task(self._consume_generator(gen, ws))

    async def _consume_generator(self, gen: Any, ws: WebSocket | None = None) -> None:
        try:
            if inspect.isasyncgen(gen):
                async for _ in gen:
                    await self.broadcast_updates(ws=ws)
            elif inspect.isgenerator(gen):
                try:
                    while True:
                        next(gen)
                        await self.broadcast_updates(ws=ws)
                except StopIteration:
                    pass
        except Exception as e:
            error_trace: str = traceback.format_exc()
            error_msg: str = f"Error in on_mount generator: {str(e)}\n{error_trace}"
            print(error_msg)
            logger.error(error_msg)
            err_payload: str = _obf_dumps(
                {
                    "action": "error",
                    "traceback": error_trace if self.debug else "Internal Server Error",
                    "callback_id": None,
                    "result": None,
                },
                getattr(self, "parano_key", None),
            )
            has_sent = False
            for queue in self.sse_queues:
                queue.put_nowait(err_payload)
                has_sent = True
            dead_ws = []
            for client in list(self.websockets):
                try:
                    await client.send_text(err_payload)
                    has_sent = True
                except Exception:
                    dead_ws.append(client)
            for client in dead_ws:
                self.websockets.discard(client)
            
            if not has_sent:
                self._push_to_fallback(err_payload)

    def update(self) -> None:
        """
        Schedules a broadcast of all pending updates in the next event loop iteration.
        This provides a throttled, asynchronous update mechanism that can be safely
        triggered from both synchronous and asynchronous code.
        """
        if not getattr(self, "_update_scheduled", False):
            try:
                loop = asyncio.get_running_loop()
                self._update_scheduled = True
                loop.call_soon(self._do_update)
            except RuntimeError:
                # No running loop (might happen during early initialization)
                pass

    def _do_update(self) -> None:
        """Internal callback to handle the actual broadcast after call_soon."""
        self._update_scheduled = False
        asyncio.create_task(self.broadcast_updates())

    async def broadcast_updates(
        self, result: Any = None, callback_id: str | None = None, ws: WebSocket | None = None
    ) -> None:
        """
        Collects all pending updates (tags, JS calls, statics)
        and broadcasts them to all connected clients.
        Optional 'result' and 'callback_id' are used to resolve client-side Promises.
        """
        updates: dict[str, str] = {}
        js_calls: list[str] = []

        try:
            self.collect_updates(self, updates, js_calls)
        except Exception as e:
            error_trace = traceback.format_exc()
            error_msg = (
                f"Error during render/update collection: {str(e)}\n{error_trace}"
            )
            print(error_msg)
            logger.error(error_msg)

            err_payload = _obf_dumps(
                {
                    "action": "error",
                    "traceback": error_trace if self.debug else "Internal Server Error",
                    "callback_id": callback_id,
                    "result": None,
                },
                getattr(self, "parano_key", None),
            )

            has_sent = False
            # Send to websocket clients
            dead_ws: list[WebSocket] = []
            for client in list(self.websockets) + ([ws] if ws and ws not in self.websockets else []):
                try:
                    await client.send_text(err_payload)
                    has_sent = True
                except Exception:
                    dead_ws.append(client)
            for client in dead_ws:
                self.websockets.discard(client)

            # Send to SSE clients
            for queue in self.sse_queues:
                queue.put_nowait(err_payload)
                has_sent = True

            if not has_sent:
                self._push_to_fallback(err_payload)

            return  # Abort sending normal updates

        all_statics: list[str] = []
        self.collect_statics(self, all_statics)

        new_statics = [s for s in all_statics if s not in self.sent_statics]

        if updates or js_calls or new_statics or callback_id:
            self.sent_statics.update(new_statics)

            data = {
                "action": "update",
                "updates": updates,
                "js": js_calls,
                "statics": new_statics,
            }
            if callback_id:
                data["callback_id"] = callback_id
                data["result"] = result

            logger.debug(
                "Broadcasting updates: %s (js calls: %d, result: %s)",
                list(updates.keys()),
                len(js_calls),
                result if callback_id else "n/a",
            )

            payload = _obf_dumps(data, getattr(self, "parano_key", None))

            has_sent = False
            # Send to websocket clients
            dead_ws_clients: list[WebSocket] = []
            for client in list(self.websockets) + ([ws] if ws and ws not in self.websockets else []):
                try:
                    await client.send_text(payload)
                    has_sent = True
                except Exception:
                    dead_ws_clients.append(client)
            for client in dead_ws_clients:
                self.websockets.discard(client)

            # Send to SSE clients
            for queue in self.sse_queues:
                queue.put_nowait(payload)
                has_sent = True
                
            if not has_sent:
                self._push_to_fallback(payload)

    def render_tag(self, tag: GTag) -> str:
        """
        Renders a GTag to its HTML string representation.
        Before rendering, it injects 'htag_event' calls into HTML event attributes,
        enabling the bridge between DOM events and Python callbacks.
        """

        def process(t: GTag) -> None:
            if isinstance(t, GTag):
                with t._GTag__lock:
                    # Auto-inject oninput for inputs if not already there, to support auto-binding
                    if (
                        t.tag in ["input", "textarea", "select"]
                        and "input" not in t._get_events()
                    ):
                        t._get_attrs()["oninput"] = (
                            f"htag_event('{t.id}', 'input', event)"
                        )
                    t._reset_dirty()  # Clear dirty flag after rendering
                    for child in t.childs:
                        if isinstance(child, GTag):
                            process(child)

        process(tag)
        return str(tag)

    def find_tag(self, root: GTag, tag_id: str) -> GTag | None:
        """Recursively find a tag by its ID, searching both static and dynamic (reactive) children."""
        result: list[GTag | None] = [None]

        def visitor(t: GTag) -> None:
            if result[0] is None and (t.id == tag_id or t._get_attrs().get("id") == tag_id):
                result[0] = t

        self._walk_tree(root, visitor)
        return result[0]


# Register AppRunner as App to allow Tag.App(...) builder
Tag._registry["App"] = AppRunner
Tag.App = AppRunner  # type: ignore
