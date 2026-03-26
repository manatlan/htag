from __future__ import annotations

import inspect
import logging
import os
import platform
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Any, Callable
import threading
import uvicorn

if TYPE_CHECKING:
    from ..core import App
    from ..runner import AppRunner as App
    from ..web import WebApp

logger = logging.getLogger("htag")


class ChromeApp:
    """
    Executes an App in a Chrome/Chromium kiosk window.
    Features auto-cleanup of temporary browser profiles.
    """

    def __init__(
        self,
        app: type[App] | App,
        kiosk: bool = True,
        width: int = 800,
        height: int = 600,
        debug: bool = True,
    ):
        self.app = app
        self.kiosk = kiosk
        self.width = width
        self.height = height
        self.debug = debug
        self._cleanup_func: Callable[[], None] | None = None

    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        reload: bool = False,
        **kwargs: Any,
    ) -> None:
        if port == 0:
            if "HTAG_PORT" in os.environ:
                port = int(os.environ["HTAG_PORT"])
            else:
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, 0))
                    port = s.getsockname()[1]
                os.environ["HTAG_PORT"] = str(port)

        if reload:
            # Tag the app so the frontend knows to auto-reconnect
            if inspect.isclass(self.app):
                self.app._reload = True
            else:
                setattr(self.app, "_reload", True)

        is_reloader_child = os.environ.get("HTAG_RELOADER", "") == "1"

        if self.kiosk and not (reload and is_reloader_child):
            # Only launch the browser if we are NOT the restarted child worker
            def launch() -> None:
                time.sleep(1)  # Give the server a second to start

                import tempfile
                import shutil
                import atexit

                tmp_dir = tempfile.mkdtemp(prefix="htag_")

                def cleanup() -> None:
                    try:
                        shutil.rmtree(tmp_dir)
                        logger.info("Cleaned up temporary browser profile: %s", tmp_dir)
                    except Exception:
                        pass

                atexit.register(cleanup)
                self._cleanup_func = cleanup

                browsers: list[str] = []
                if platform.system() == "Windows":
                    # Windows-specific browser paths
                    possible_paths = [
                        os.path.join(
                            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                            "Google",
                            "Chrome",
                            "Application",
                            "chrome.exe",
                        ),
                        os.path.join(
                            os.environ.get(
                                "PROGRAMFILES(X86)", "C:\\Program Files (x86)"
                            ),
                            "Google",
                            "Chrome",
                            "Application",
                            "chrome.exe",
                        ),
                        os.path.join(
                            os.environ.get("LOCALAPPDATA", ""),
                            "Google",
                            "Chrome",
                            "Application",
                            "chrome.exe",
                        ),
                        os.path.join(
                            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                            "Microsoft",
                            "Edge",
                            "Application",
                            "msedge.exe",
                        ),
                        os.path.join(
                            os.environ.get(
                                "PROGRAMFILES(X86)", "C:\\Program Files (x86)"
                            ),
                            "Microsoft",
                            "Edge",
                            "Application",
                            "msedge.exe",
                        ),
                        os.path.join(
                            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
                            "BraveSoftware",
                            "Brave-Browser",
                            "Application",
                            "brave.exe",
                        ),
                        os.path.join(
                            os.environ.get("LOCALAPPDATA", ""),
                            "BraveSoftware",
                            "Brave-Browser",
                            "Application",
                            "brave.exe",
                        ),
                    ]
                    browsers = [p for p in possible_paths if os.path.isfile(p)]
                else:
                    # Linux/macOS browser names
                    browsers = [
                        "google-chrome-stable",
                        "google-chrome",
                        "chromium-browser",
                        "chromium",
                        "chrome",
                        "microsoft-edge",
                        "brave-browser",
                    ]

                found = False
                for browser in browsers:
                    try:
                        subprocess.Popen(
                            [
                                browser,
                                f"--app=http://{host}:{port}",
                                f"--window-size={self.width},{self.height}",
                                f"--user-data-dir={tmp_dir}",
                                "--no-first-run",
                                "--no-default-browser-check",
                            ],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        logger.info(
                            "Launched %s with window size %dx%d",
                            browser,
                            self.width,
                            self.height,
                        )
                        found = True
                        break
                    except FileNotFoundError:
                        continue
                    except Exception as e:
                        logger.error("Error launching %s: %s", browser, e)
                        continue

                if not found:
                    logger.warning(
                        "Could not launch any Chromium-based browser (tried: %s)",
                        ", ".join(browsers),
                    )
                    import webbrowser

                    if webbrowser.open(f"http://{host}:{port}"):
                        logger.info("Fallback: opened default browser")
                    else:
                        logger.error("Fatal: Could not open any browser at all")

            threading.Thread(target=launch, daemon=True).start()

        if reload and not is_reloader_child:
            # Start the reloader loop
            from ..runner import Reloader
            Reloader.run_with_reloader()
            return

        from ..runner import AppRunner as App
        from ..web import WebApp

        def on_inst(inst: App) -> None:
            inst.exit_on_disconnect = True
            if self._cleanup_func:
                # Use object.__setattr__ to bypass GTag.__setattr__ and avoid deprecation warning
                object.__setattr__(inst, "_browser_cleanup", self._cleanup_func)

        if not inspect.isclass(self.app):
            self.app.exit_on_disconnect = True

        ws = WebApp(self.app, on_instance=on_inst, debug=self.debug)
        log_config = (
            None if getattr(sys, "frozen", False) else uvicorn.config.LOGGING_CONFIG
        )
        uvicorn.run(ws.app, host=host, port=port, log_config=log_config)
