from __future__ import annotations

import inspect
import json
import logging
import sys
from typing import Any

from ..server import App

logger = logging.getLogger("htag")

if "pyodide" in sys.modules or "pyscript" in sys.modules:
    import js  # type: ignore
    from pyodide.ffi import create_proxy  # type: ignore
else:
    js = None

    def create_proxy(f: Any) -> Any:
        return f


HTAG_PYSCRIPT_JS = """
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
if (!customElements.get('htag-error')) {
    customElements.define('htag-error', HtagError);
}

if (!window._error_overlay) {
    window._error_overlay = document.createElement('htag-error');
    document.body.appendChild(window._error_overlay);
    window.onerror = function(message, source, lineno, colno, error) {
        if(window._error_overlay && typeof window._error_overlay.show === 'function') {
            window._error_overlay.show("Client JavaScript Error", `${message}\\n${source}:${lineno}:${colno}\\n${error ? error.stack : ''}`);
        }
    };
    window.onunhandledrejection = function(event) {
        if(window._error_overlay && typeof window._error_overlay.show === 'function') {
            window._error_overlay.show("Unhandled Promise Rejection", String(event.reason));
        }
    };
}

window._htag_callbacks = {};

window.htag_event = function(id, event_name, event) {
    var callback_id = Math.random().toString(36).substring(2);
    event = event || {};
    
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
    
    // Call PyScript runner proxy
    if (window.py_htag_event) {
        window.py_htag_event(JSON.stringify(payload));
    } else {
        console.error("PyScript htag_event proxy not found! Cannot send event to Python.");
    }

    return new Promise(resolve => {
        window._htag_callbacks[callback_id] = resolve;
    });
};

window.handle_payload = function(data) {
    if (data.action === "update") {
        for(var id in data.updates) {
            var el = document.getElementById(id);
            if(el) el.outerHTML = data.updates[id];
        }
        // Ensure overlay is still in the DOM (in case the body was replaced)
        if(window._error_overlay && window._error_overlay.parentNode !== document.body) {
            document.body.appendChild(window._error_overlay);
        }
        if(data.js) {
            for(var i=0; i<data.js.length; i++) eval(data.js[i]);
        }
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
        if(data.callback_id && window._htag_callbacks[data.callback_id]) {
            window._htag_callbacks[data.callback_id](data.result);
            delete window._htag_callbacks[data.callback_id];
        }
    } else if (data.action === "error") {
        if(window._error_overlay && window._error_overlay.show) {
            window._error_overlay.show("Server Error", data.traceback);
        } else {
            console.error("Server Error:", data.traceback);
        }
    }
};
"""


class DummyWS:
    """
    Mocks Starlette's WebSocket for PyScript environment.
    App passes _obf_dumps payload here.
    """

    async def send_text(self, text: str) -> None:
        if js is not None:
            # We don't use encryption in PyScript.
            payload = js.JSON.parse(text)
            js.window.handle_payload(payload)


class PyScript:
    """
    Executes an App inside a PyScript SPA.
    No backend server utilized; all htag logic renders natively into DOM.
    """

    def __init__(self, app: type[App] | App, debug: bool = True):
        if js is None:
            raise RuntimeError(
                "PyScript runner can only be used inside a PyScript/Pyodide environment."
            )

        self.app_cls_or_inst = app
        self.debug = debug

    def run(self, window: Any = None) -> None:
        """
        Initializes the PyScript app and runs it, wrapping document.body.
        """
        if inspect.isclass(self.app_cls_or_inst):
            self.app = self.app_cls_or_inst()
        else:
            self.app = self.app_cls_or_inst

        self.app.debug = self.debug
        self.app.parano_key = None  # No encryption inside SPA

        self._dummy_ws = DummyWS()
        self.app.websockets = {self._dummy_ws}

        # Setup JS environment
        self._proxy = create_proxy(self._handle_event)
        js.window.py_htag_event = self._proxy

        js.eval(HTAG_PYSCRIPT_JS)

        # Generate initial DOM (HTML body)
        try:
            body_html = self.app.render_initial()
        except Exception as e:
            import traceback

            error_trace = traceback.format_exc()
            safe_trace = error_trace.replace("`", "\\`")
            logger.error("Error during initial render: %s\n%s", e, error_trace)
            body_html = f"<body><htag-error show='true'></htag-error><script>document.querySelector('htag-error').show('Initial Render Error', `{safe_trace}`);</script></body>"

        # Inject original statics
        statics: list[str] = []
        self.app.collect_statics(self.app, statics)
        self.app.sent_statics = set(statics)
        for s in statics:
            safe_s = s.replace("`", "\\`")
            js.eval(
                f"""
            var div = document.createElement('div');
            div.innerHTML = `{safe_s}`;
            var node = div.firstChild;
            if(node && (node.tagName === "STYLE" || node.tagName === "LINK")) {{
                document.head.appendChild(node);
            }}
            """
            )

        # Inject into the PyScript HTML Page
        # Replace the `<body>...</body>` with our App's render!
        js.document.body.outerHTML = body_html

        # Ensure overlay is still in the DOM (in case the body was replaced)
        js.document.body.appendChild(js.window._error_overlay)

        self.app._trigger_mount()

    def _handle_event(self, msg_str: str) -> None:
        """Called directly from JS bridge."""
        import asyncio

        msg = json.loads(msg_str)
        asyncio.create_task(self.app.handle_event(msg, self._dummy_ws))  # type: ignore
