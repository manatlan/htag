from __future__ import annotations
from .logo import LOGO_PNG_B64

import asyncio
import json
import logging
import os
import sys
import threading
import traceback
import uuid
import inspect
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
from .core import GTag, current_request

logger = logging.getLogger("htag")

# Embedded logo (PNG base64 encoded)


class Event:
    """
    Simulates a DOM Event.
    Attributes are dynamically populated from the client message.
    """

    def __init__(self, target: GTag, msg: dict[str, Any]) -> None:
        self.target = target
        self.id: str = msg.get("id", "")
        self.name: str = msg.get("event", "")
        # Flat access to msg['data'] (e.g., e.value, e.x, etc.)
        for k, v in msg.get("data", {}).items():
            setattr(self, k, v)

    def __getattr__(self, name: str) -> Any:
        return None

    def __repr__(self) -> str:
        return f"Event({self.name} on {self.target.tag})"


def _obf_dumps(obj: Any, key: str | None) -> str:
    if key:
        import base64

        bdata = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
        bkey = key.encode("utf-8")
        res = bytearray(len(bdata))
        for i in range(len(bdata)):
            res[i] = bdata[i] ^ bkey[i % len(bkey)]
        return base64.b64encode(res).decode("ascii")
    return json.dumps(obj)


def _obf_loads(data: str, key: str | None) -> Any:
    if key:
        import base64

        bdata = base64.b64decode(data)
        bkey = key.encode("utf-8")
        res = bytearray(len(bdata))
        for i in range(len(bdata)):
            res[i] = bdata[i] ^ bkey[i % len(bkey)]
        return json.loads(res.decode("utf-8"))
    return json.loads(data)


CLIENT_JS = """
// The client-side bridge that connects the browser to the Python server.
var ws;
var use_fallback = false;
var sse;
var _base_path = window.location.pathname.endsWith("/") ? window.location.pathname : window.location.pathname + "/";
window._htag_callbacks = {}; // Store promise resolvers

// --- htag-error Web Component (Shadow DOM for style isolation) ---
class HtagError extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({mode: 'open'});
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 2147483647;
                    align-items: center;
                    justify-content: center;
                    backdrop-filter: blur(2px);
                }
                :host([show]) { display: flex; }
                .dialog {
                    width: 80%;
                    max-width: 600px;
                    background: #fee2e2;
                    border: 1px solid #ef4444;
                    border-left: 5px solid #ef4444;
                    color: #991b1b;
                    padding: 15px;
                    border-radius: 4px;
                    font-family: system-ui, -apple-system, sans-serif;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
                    max-height: 80vh;
                    overflow-y: auto;
                    text-align: left;
                    position: relative;
                }
                h3 { margin: 0 0 10px 0; font-size: 16px; display: inline-block;}
                pre { background: #fef2f2; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto; margin:0; text-align: left; }
                .close { position: absolute; top: 10px; right: 15px; cursor: pointer; font-weight: bold; font-size: 18px; color: #ef4444; }
                .close:hover { color: #b91c1c; }
                .copy { float: right; margin-right: 40px; cursor: pointer; background: #ef4444; color: white; border: none; padding: 2px 8px; border-radius: 3px; font-size: 12px; transition: background 0.2s; }
                .copy:hover { background: #b91c1c; }
                .copy:active { background: #991b1b; }
            </style>
            <div class="dialog">
                <div class="close" title="Close">×</div>
                <button class="copy" id="copy-btn">Copy</button>
                <h3 id="title">Error</h3>
                <pre id="trace"></pre>
            </div>
        `;
        this.shadowRoot.querySelector('.close').onclick = () => this.removeAttribute('show');
        this.shadowRoot.getElementById('copy-btn').onclick = () => {
            const trace = this.shadowRoot.getElementById('trace').textContent;
            navigator.clipboard.writeText(trace).then(() => {
                const btn = this.shadowRoot.getElementById('copy-btn');
                const old = btn.textContent;
                btn.textContent = 'Copied!';
                setTimeout(() => btn.textContent = old, 1500);
            });
        };
    }
    show(title, trace) {
        this.shadowRoot.getElementById('title').textContent = title;
        this.shadowRoot.getElementById('trace').textContent = trace || 'No traceback available.';
        this.setAttribute('show', '');
    }
}
customElements.define('htag-error', HtagError);

// Global references for UI overlays
var _error_overlay = document.createElement('htag-error');

document.addEventListener("DOMContentLoaded", () => {
    document.body.appendChild(_error_overlay);
});

window.onerror = function(message, source, lineno, colno, error) {
    if(_error_overlay && typeof _error_overlay.show === 'function') {
        _error_overlay.show("Client JavaScript Error", `${message}\\n${source}:${lineno}:${colno}\\n${error ? error.stack : ''}`);
    }
};
window.onunhandledrejection = function(event) {
    if(_error_overlay && typeof _error_overlay.show === 'function') {
        _error_overlay.show("Unhandled Promise Rejection", String(event.reason));
    }
};

function _enc(obj) {
    if(window.PARANO) {
        var str = unescape(encodeURIComponent(JSON.stringify(obj)));
        var res = "";
        for(var i=0; i<str.length; i++) res += String.fromCharCode(str.charCodeAt(i) ^ window.PARANO.charCodeAt(i % window.PARANO.length));
        return btoa(res);
    }
    return JSON.stringify(obj);
}

function _dec(b64) {
    if(window.PARANO) {
        var str = atob(b64);
        var res = "";
        for(var i=0; i<str.length; i++) res += String.fromCharCode(str.charCodeAt(i) ^ window.PARANO.charCodeAt(i % window.PARANO.length));
        return JSON.parse(decodeURIComponent(escape(res)));
    }
    return JSON.parse(b64);
}

function init_ws() {
    var ws_protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
    ws = new WebSocket(ws_protocol + window.location.host + _base_path + "ws");
    
    ws.onopen = function() {
        console.log("htag: websocket connected");
    };

    ws.onmessage = function(event) {
        var data = _dec(event.data);
        handle_payload(data);
    };

    ws.onerror = function(err) {
        console.warn("htag: websocket error, switching to HTTP fallback (SSE)", err);
        fallback();
    };

    ws.onclose = function(event) {
        // If it closes abnormally or very quickly, trigger fallback
        if (event.code !== 1000 && event.code !== 1001) {
             console.warn("htag: websocket closed unexpectedly, switching to HTTP fallback (SSE)", event);
             fallback();
        }
    };
}

function handle_payload(data) {
    if(data.action == "update") {
        // Apply partial DOM updates received from the server
        for(var id in data.updates) {
            var el = document.getElementById(id);
            if(el) el.outerHTML = data.updates[id];
        }
        
        // Ensure overlays are still in the DOM (in case the body was replaced)
        if(_error_overlay && _error_overlay.parentNode !== document.body) {
            document.body.appendChild(_error_overlay);
        }
        // Execute any JavaScript calls emitted by the Python tags
        if(data.js) {
            for(var i=0; i<data.js.length; i++) eval(data.js[i]);
        }
        // Inject new css/js statics if they haven't been loaded yet
        if(data.statics) {
            data.statics.forEach(s => {
                var div = document.createElement('div');
                div.innerHTML = s.trim();
                var node = div.firstChild;
                if (node && (node.tagName === "STYLE" || node.tagName === "LINK")) {
                    document.head.appendChild(node);
                }
            });
        }
        // Resolve promise if a result is returned for a callback
        if(data.callback_id && window._htag_callbacks[data.callback_id]) {
            window._htag_callbacks[data.callback_id](data.result);
            delete window._htag_callbacks[data.callback_id];
        }
    } else if (data.action == "error") {
        if(_error_overlay && typeof _error_overlay.show === 'function') {
            _error_overlay.show("Server Error", data.traceback);
        } else {
            console.error("Server Error:", data.traceback);
        }
    }
}

function fallback() {
    if (use_fallback) return; 
    use_fallback = true;
    if(ws) ws.close(); // Ensure ws is torn down
    
    // Auto-reload mechanism
    if (window.HTAG_RELOAD) {
        console.log("htag: connection lost, starting auto-reload polling...");
        
        function poll_reload() {
            fetch("/").then(response => {
                if (response.ok) {
                    console.log("htag: server is back! Reloading page...");
                    window.location.reload();
                } else {
                    setTimeout(poll_reload, 500);
                }
            }).catch(err => {
                setTimeout(poll_reload, 500);
            });
        }
        
        setTimeout(poll_reload, 500);
        return; // Don't try SSE, we just want to reload the page when the server comes back
    }

    sse = new window.EventSource(_base_path + "stream");
    sse.onopen = () => console.log("htag: SSE connected");
    sse.onmessage = function(event) {
        handle_payload(_dec(event.data));
    };
    sse.onerror = function(err) {
        console.error("htag: SSE error", err);
        if(_error_overlay && typeof _error_overlay.show === 'function') {
            _error_overlay.show("Connection Lost", "Server Sent Events connection failed.");
        }
    };
}

// Start with WebSockets
init_ws();

// Function called by HTML 'on{event}' attributes to send interactions back to Python
// Returns a Promise that resolves with the server's return value.
function htag_event(id, event_name, event) {
    var callback_id = Math.random().toString(36).substring(2);
    event = event || {};
    
    // Determine the value to send (handle checkboxes specifically)
    var val = null;
    if (event.target) {
        if (event.target.type === 'checkbox') {
            val = event.target.checked;
        } else {
            val = event.target.value;
        }
    }
    
    var data = {
        value: val,
        key: event.key,
        pageX: event.pageX,
        pageY: event.pageY,
        callback_id: callback_id
    };
    var payload = {id: id, event: event_name, data: data};
    
    if(!use_fallback && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(_enc(payload));
    } else {
        // Use HTTP POST Fallback
        // (Fastest trigger even if SSE is still initializing)
        if (!use_fallback) fallback();
        fetch(_base_path + "event", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: _enc(payload)
        }).then(response => {
            if (!response.ok) {
                if(_error_overlay && typeof _error_overlay.show === 'function') {
                    _error_overlay.show("HTTP Error", `Server returned status: ${response.status}`);
                }
            }
        }).catch(err => {
            console.error("htag event POST error:", err);
            if(_error_overlay && typeof _error_overlay.show === 'function') {
                _error_overlay.show("Network Error", "Could not reach server to trigger event.");
            }
        });
    }

    return new Promise(resolve => {
        window._htag_callbacks[callback_id] = resolve;
    });
}
"""

# --- WebApp ---


class WebApp:
    """
    Starlette implementation for hosting one or more App sessions.
    Handles the HTTP initial render and the WebSocket communication.
    """

    def __init__(
        self,
        tag_entity: type[App] | App,
        on_instance: Callable[[App, Request | WebSocket], None] | None = None,
        debug: bool = True,
        parano: bool = False,
    ) -> None:
        self._lock = threading.Lock()
        self.tag_entity = tag_entity  # Class or Instance
        self.on_instance = on_instance  # Optional callback(instance)
        self.debug = debug
        self.exit_on_disconnect = False
        self.parano_key = os.urandom(8).hex() if parano else None
        self.instances: dict[str, App] = {}  # sid -> App instance
        self.app = Starlette()
        self._setup_routes()

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        open_browser: bool = True,
        exit_on_disconnect: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Runs the WebApp using uvicorn.
        """
        import uvicorn

        self.exit_on_disconnect = exit_on_disconnect

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

    def _get_instance(self, sid: str, request_or_ws: Request | WebSocket) -> "App":
        if sid not in self.instances:
            with self._lock:
                if sid not in self.instances:
                    token = current_request.set(request_or_ws)
                    try:
                        if inspect.isclass(self.tag_entity):
                            self.instances[sid] = self.tag_entity()
                            logger.info("Created new session instance for sid: %s", sid)
                        else:
                            # tag_entity is an App instance
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
                        setattr(self.instances[sid], "_webserver", self)

                        # Trigger lifecycle mount on the root App instance
                        self.instances[sid]._trigger_mount()
                    finally:
                        current_request.reset(token)

        # Always update the current request object on the instance
        # to ensure session data is fresh for the current interaction
        setattr(self.instances[sid], "_request", request_or_ws)

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
                return StreamingResponse(
                    instance._handle_sse(request), media_type="text/event-stream"
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
                msg = _obf_loads(
                    msg_body.decode("utf-8"), getattr(instance, "parano_key", None)
                )
                # Run the event in the background to not block the HTTP response
                # Broadcast will trigger async queues anyway
                asyncio.create_task(instance.handle_event(msg, None))
                return JSONResponse({"status": "ok"})
            except Exception as e:
                logger.error("POST event error: %s", e)
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


# --- App ---


class App(GTag):
    """
    The main application class for htag2.
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
    def app(self) -> Starlette:
        """Property for backward compatibility: returns a Starlette instance hosting this App."""
        if not hasattr(self, "_app_host"):
            self._app_host = WebApp(self)
        return self._app_host.app

    def _render_page(self) -> str:
        # 1. Render the initial body FIRST to populate __rendered_callables
        try:
            body_html = self.render_initial()
        except Exception as e:
            error_trace = traceback.format_exc()
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
            self.collect_statics(self, all_statics)
        except Exception:
            pass  # Fatal error already caught above
        self.sent_statics.update(all_statics)
        statics_html = "".join(all_statics)

        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>{self.__class__.__name__}</title>
                <link rel="icon" href="/logo.png">
                <script>{CLIENT_JS}</script>
                <script>
                    window.HTAG_RELOAD = {"true" if getattr(self, "_reload", False) else "false"};
                    window.PARANO = {f'"{self.parano_key}"' if getattr(self, "parano_key", None) else "null"};
                </script>
                {statics_html}
            </head>
            {body_html}
        </html>
        """
        return html_content

    async def _handle_sse(self, request: Request):
        queue: asyncio.Queue = asyncio.Queue()
        self.sse_queues.add(queue)
        logger.info("New SSE connection (Total clients: %d)", len(self.sse_queues))

        # Send initial state
        try:
            updates = {self.id: self.render_initial()}
            js: list[str] = []
            self.collect_updates(self, {}, js)

            payload = _obf_dumps(
                {"action": "update", "updates": updates, "js": js},
                getattr(self, "parano_key", None),
            )
            # EventSource requires 'data: {payload}\n\n'
            yield f"data: {payload}\n\n"
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
        await websocket.accept()
        self.websockets.add(websocket)
        logger.info(
            "New WebSocket connection (Total WS clients: %d)", len(self.websockets)
        )

        # Send initial state on connection/reconnection
        try:
            updates = {self.id: self.render_initial()}
            js: list[str] = []
            self.collect_updates(self, {}, js)  # We only want the JS calls here

            await websocket.send_text(
                _obf_dumps(
                    {"action": "update", "updates": updates, "js": js},
                    getattr(self, "parano_key", None),
                )
            )
            logger.debug("Sent initial state to client")
        except Exception as e:
            logger.error("Failed to send initial state: %s", e)

        try:
            while True:
                data = await websocket.receive_text()
                msg = _obf_loads(data, getattr(self, "parano_key", None))
                await self.handle_event(msg, websocket)
        except (WebSocketDisconnect, Exception):
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
            if hasattr(self, "_webserver"):
                webserver = getattr(self, "_webserver")
                for sid, inst in webserver.instances.items():
                    if inst.websockets or inst.sse_queues:
                        active_sessions.append(f"{sid} (WS:{len(inst.websockets)}, SSE:{len(inst.sse_queues)})")

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

    def collect_statics(self, tag: GTag, result: list[str]) -> None:
        """Recursively collects statics from the whole tag tree."""

        def visitor(t: GTag) -> None:
            s_instance = getattr(t, "statics", [])
            s_class = getattr(t.__class__, "statics", [])
            for s_list in [s_class, s_instance]:
                if not isinstance(s_list, (list, tuple)):
                    s_list = [s_list]
                for s in s_list:
                    s_str = str(s)
                    if s_str not in result:
                        result.append(s_str)

        self._walk_tree(tag, visitor)

    async def handle_event(self, msg: dict[str, Any], ws: WebSocket | None) -> None:
        tag_id: str | None = msg.get("id")
        event_name: str | None = msg.get("event")

        if not isinstance(tag_id, str):
            return

        target_tag = self.find_tag(self, tag_id)
        if target_tag:
            callback_id = msg.get("data", {}).get("callback_id")
            # Auto-sync value from client (bypass __setattr__ to avoid re-rendering the input while typing)
            if "value" in msg.get("data", {}):
                target_tag._set_attr_direct("value", msg["data"]["value"])

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
                    await self.broadcast_updates(result=res, callback_id=callback_id)
                except Exception as e:
                    error_trace: str = traceback.format_exc()
                    error_msg: str = (
                        f"Error in {event_name} callback: {str(e)}\n{error_trace}"
                    )
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

                    if ws:
                        try:
                            await ws.send_text(err_payload)
                        except Exception:
                            pass
                    else:
                        # Fallback Mode: Trigger error broadcast through SSE
                        for queue in self.sse_queues:
                            queue.put_nowait(err_payload)

                    return
            else:
                res = None
                await self.broadcast_updates(result=res, callback_id=callback_id)

    async def broadcast_updates(
        self, result: Any = None, callback_id: str | None = None
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

            # Send to websocket clients
            dead_ws: list[WebSocket] = []
            for client in list(self.websockets):
                try:
                    await client.send_text(err_payload)
                except Exception:
                    dead_ws.append(client)
            for client in dead_ws:
                self.websockets.discard(client)

            # Send to SSE clients
            for queue in self.sse_queues:
                queue.put_nowait(err_payload)

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

            # Send to websocket clients
            dead_ws_clients: list[WebSocket] = []
            for client in list(self.websockets):
                try:
                    await client.send_text(payload)
                except Exception:
                    dead_ws_clients.append(client)
            for client in dead_ws_clients:
                self.websockets.discard(client)

            # Send to SSE clients
            for queue in self.sse_queues:
                queue.put_nowait(payload)

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
            if result[0] is None and t.id == tag_id:
                result[0] = t

        self._walk_tree(root, visitor)
        return result[0]


from .core import Tag  # noqa: E402

Tag._registry["App"] = App
