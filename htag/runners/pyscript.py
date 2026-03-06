from __future__ import annotations

import inspect
import json
import logging
import sys
from ..runner import AppRunner as App

logger = logging.getLogger("htag")

if "pyodide" in sys.modules or "pyscript" in sys.modules:
    import js  # type: ignore
    from pyodide.ffi import create_proxy  # type: ignore
else:
    js = None

    def create_proxy(f: Any) -> Any:
        return f


from ..client_js import CLIENT_JS

HTAG_PYSCRIPT_JS = """
// Tell standard JS not to connect WebSockets since we are in a PyScript SPA
window.HTAG_EXT_INIT = true;

// Define custom transport for PyScript to route directly to Python instead of WS/HTTP
window.htag_transport = function(payload) {
    if (window.py_htag_event) {
        window.py_htag_event(JSON.stringify(payload));
    } else {
        console.error("PyScript htag_event proxy not found! Cannot send event to Python.");
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

        # Setup PyScript specific transport configuration FIRST
        js.eval(HTAG_PYSCRIPT_JS)
        # Then evaluate generic HTAG client logic
        js.eval(CLIENT_JS)

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
