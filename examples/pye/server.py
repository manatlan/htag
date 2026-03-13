"""
Pye Server: A dynamic, file-based htag application server.

This server automatically discovers htag applications (classes named 'App' inheriting from Tag.App),
manages their lifecycle (hot-reload on change, auto-unload on TTL), and provides a robust
routing system for:
1. Htag Applications (mounted at their file/folder path)
2. Standalone Python Scripts (executed via a runner, supporting extensionless URLs)
3. Static Files (served directly)
4. Directory Indexing (auto-generated listing with metadata)

Special App-level configurations supported:
- App._parano_ = True: Enables htag parano mode (obfuscated data flow)
- App._ttl_ = 0: Disables auto-unloading for persistent applications
- App._ttl_ = <seconds>: Custom time-to-live for memory management
"""

import ast
import asyncio
import importlib
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Type

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse
from starlette.types import Receive, Scope, Send

from htag import Tag
from htag.server import WebApp

# Global configuration and logging
logger = logging.getLogger("pye")
APP_TTL = 10 * 60  # Default memory life: 10 minutes


def get_app_mtime(p: Path) -> float:
    """
    Calculate the maximum modification time for an htag application.
    For packages (__init__.py), it recursive scans all internal .py files.
    """
    if p.is_file():
        if p.name == "__init__.py":
            try:
                # Get the newest mtime among all python files in the package
                return max(
                    (f.stat().st_mtime for f in p.parent.rglob("*.py")),
                    default=p.stat().st_mtime,
                )
            except Exception:
                pass
        return p.stat().st_mtime
    return 0.0


def load_htag_app(mod_path: str) -> Type[Tag.App] | None:
    """
    Dynamically load or reload a python module and extract the 'App' class.
    Ensures the extracted class is a valid htag.Tag.App subclass.
    """
    try:
        # Reloading allows 'hot-reload' behavior without restarting the server
        if mod_path in sys.modules:
            mod = importlib.reload(sys.modules[mod_path])
        else:
            mod = importlib.import_module(mod_path)
            
        app_class = getattr(mod, "App", None)
        if (
            app_class
            and isinstance(app_class, type)
            and issubclass(app_class, Tag.App)
        ):
            return app_class
        logger.warning(f"Module '{mod_path}' does not contain a valid 'App' class")
    except Exception as e:
        logger.error(f"Failed to load module '{mod_path}': {e}", exc_info=True)
    return None


def looks_like_htag_app(p: Path) -> bool:
    """
    Perform a shallow AST analysis to check if a file contains an htag 'App' class.
    This is much faster and safer than importing every file found during discovery.
    """
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in tree.body:
            # Matches: class App(Tag.App): ...
            if isinstance(node, ast.ClassDef) and node.name == "App":
                return True
            # Matches: App = SomeClass
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "App":
                        return True
    except Exception:
        pass
    return False


@dataclass
class AppInfo:
    """
    Data container for a discovered htag application and its operational state.
    """
    app: Starlette | None      # The instantiated Starlette WebApp (None if not loaded)
    file: Path                 # Primary file path (entrypoint)
    mtime: float               # Last known mtime (used for reload check)
    mod_path: str              # Python import path (e.g. www.myapp)
    last_accessed: float       # Timestamp of the last interaction (for TTL)
    ttl: float | None = None   # Custom TTL from App class attribute


class AppDiscoverer:
    """
    Service responsible for recursive filesystem scanning to find htag apps.
    """
    def __init__(self, apps_dir: Path):
        self.apps_dir = apps_dir
        self.logger = logger.getChild("discovery")

    def discover(self) -> dict[str, AppInfo]:
        """
        Scan the target directory recursively for htag applications.
        Returns a mapping of relative path strings to AppInfo objects.
        """
        found_apps: dict[str, AppInfo] = {}
        self.logger.info(f"Scanning directory: {self.apps_dir}")
        
        def crawl(current_dir: Path, rel_root: str = "") -> None:
            for p in current_dir.iterdir():
                # Ignore hidden files and python caches
                if p.name == "__pycache__" or p.name.startswith("."):
                    continue

                rel_path = f"{rel_root}/{p.name}" if rel_root else p.name

                if p.is_dir():
                    # Check if it's a package app (folder with __init__.py containing App)
                    init_file = p / "__init__.py"
                    if init_file.exists() and looks_like_htag_app(init_file):
                        mod_path = f"www.{rel_path.replace('/', '.')}"
                        self.logger.info(f"Discovered package app: {rel_path} ({mod_path})")
                        found_apps[rel_path] = AppInfo(
                            app=None, file=init_file, mtime=0.0,
                            mod_path=mod_path, last_accessed=time.time(),
                        )
                        continue # Don't crawl inside a package app folder
                    crawl(p, rel_path)
                elif p.is_file() and p.name.endswith(".py") and p.name != "__init__.py" and looks_like_htag_app(p):
                    # Check for standalone file apps
                    app_name = rel_path[:-3]
                    mod_path = f"www.{app_name.replace('/', '.')}"
                    self.logger.info(f"Discovered file app: {app_name} ({mod_path})")
                    found_apps[app_name] = AppInfo(
                        app=None, file=p, mtime=0.0,
                        mod_path=mod_path, last_accessed=time.time(),
                    )

        if self.apps_dir.exists() and self.apps_dir.is_dir():
            crawl(self.apps_dir)

        self.logger.info(f"Discovery complete. Found {len(found_apps)} apps.")
        return found_apps


class IndexGenerator:
    """
    Utility to generate dynamic HTML directory listings (Auto-index).
    """
    @staticmethod
    def generate(apps_dir: Path, apps: dict[str, AppInfo], prefix: str = "") -> str:
        """Generates a responsive HTML directory listing for the given prefix."""
        target_dir = apps_dir / prefix
        if not target_dir.is_dir(): return ""

        items: list[str] = []
        if prefix:
            # Add 'Parent Directory' link
            parent = str(Path(prefix).parent)
            parent_link = f"/{parent}/" if parent != "." else "/"
            items.append(f'<li>📁 <a href="{parent_link}">.. (Parent Directory)</a></li>')

        folders, htag_apps, scripts, statics = [], [], [], []
        for p in sorted(target_dir.iterdir()):
            if p.name == "__pycache__" or p.name.startswith("."): continue
            
            rel_item = f"{prefix}/{p.name}" if prefix else p.name
            if p.is_dir():
                if (p / "__init__.py").is_file() and rel_item in apps:
                    htag_apps.append(p.name)
                else:
                    folders.append(p.name)
            else:
                if p.name == "__init__.py": continue
                if p.name.endswith(".py"):
                    # Classify between htag App and simple Script
                    if rel_item[:-3] in apps: htag_apps.append(p.name[:-3])
                    else: scripts.append(p.name[:-3])
                else:
                    statics.append(p.name)

        def link(name, is_dir=False):
            # Construct URL for the item
            base = f"/{prefix}/{name}" if prefix else f"/{name}"
            return base + ("/" if is_dir else "")

        # Assembly logic
        for f in sorted(folders): items.append(f'<li>📁 <a href="{link(f, True)}">{f}/</a></li>')
        for a in sorted(htag_apps): items.append(f'<li>🚀 <a href="{link(a, True)}">{a}</a> <small style="color:#888">(htag App)</small></li>')
        for s in sorted(scripts): items.append(f'<li>🐍 <a href="{link(s)}">{s}</a> <small style="color:#888">(Script)</small></li>')
        for s in sorted(statics): items.append(f'<li>📄 <a href="{link(s)}">{s}</a></li>')

        title = f"Index of {prefix}/" if prefix else "Root Index"
        content = f'<ul style="list-style-type: none; padding-left: 10px;">{"".join(items)}</ul>' if items else "<p>No entries found.</p>"
        return f"<html><head><title>{title}</title><style>body {{ font-family: sans-serif; padding:20px; }} li {{ margin: 6px 0; }} a {{ text-decoration: none; color: #0366d6; font-size: 16px; }} a:hover {{ text-decoration: underline; }}</style></head><body><h1>{title}</h1>{content}</body></html>"


class ScriptRunner:
    """
    Executes standalone Python scripts in a separate process,
    capturing stdout/stderr and passing basic HTTP environment variables.
    """
    @staticmethod
    async def run(full_path: Path, scope: Scope) -> HTMLResponse:
        """Run a .py file and return its output as an HTML response."""
        script_logger = logger.getChild("script")
        script_name = full_path.name
        script_logger.info(f"Executing script: {script_name}")
        
        try:
            env = os.environ.copy()
            if scope["type"] == "http":
                env.update({
                    "QUERY_STRING": scope.get("query_string", b"").decode("utf-8", "ignore"),
                    "REQUEST_METHOD": scope.get("method", "GET"),
                    "PATH_INFO": scope["path"],
                })

            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(full_path),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10.0)
            
            if stderr:
                script_logger.warning(f"Script '{script_name}' stderr: {stderr.decode('utf-8', errors='replace')}")

            if proc.returncode == 0:
                return HTMLResponse(stdout.decode("utf-8", errors="replace"))
            
            return HTMLResponse(
                f"<html><body><h1>Script Error</h1><pre>{stderr.decode('utf-8', errors='replace')}</pre></body></html>",
                status_code=500
            )
        except asyncio.TimeoutError:
            script_logger.error(f"Script '{script_name}' timed out")
            return HTMLResponse("<html><body><h1>Script Timeout</h1></body></html>", status_code=504)
        except Exception as e:
            script_logger.error(f"Failed to execute script '{script_name}': {e}", exc_info=True)
            return HTMLResponse(f"Execution failed: {e}", status_code=500)


class DynamicHtagApps:
    """
    The main routing engine for Pye.
    It handles dynamic discovery, lifecycle management (TTL, Hot-Reload),
    and multi-phase routing (Apps -> Files -> Auto-Index).
    """

    def __init__(self, apps_dir: str | Path, script_runner=None, auto_index=None):
        self.router_logger = logging.getLogger("pye.router")
        self.apps_dir = Path(apps_dir).resolve()
        self.script_runner = script_runner or ScriptRunner
        self.auto_index = auto_index
        self.discoverer = AppDiscoverer(self.apps_dir)
        self.apps: dict[str, AppInfo] = {}
        self._last_discovery = 0.0

    def _refresh_discovery(self):
        """Scan the filesystem and synchronize the in-memory app registry."""
        now = time.time()
        if now - self._last_discovery < 0.1: return  # Throttling
        
        self._last_discovery = now
        new_discovery = self.discoverer.discover()
        
        # Merge new findings with current state to preserve loaded instances
        for name, info in new_discovery.items():
            if name in self.apps:
                existing = self.apps[name]
                info.app = existing.app
                info.last_accessed = existing.last_accessed
                info.ttl = existing.ttl
            self.apps[name] = info
            
        # Clean up stale entries
        for name in list(self.apps.keys()):
            if name not in new_discovery:
                self.router_logger.info(f"App '{name}' removed, unloading...")
                del self.apps[name]

    def _unload_expired_apps(self):
        """Unload App instances from memory if their TTL has expired."""
        now = time.time()
        for name, info in list(self.apps.items()):
            if info.app is not None:
                ttl = info.ttl if info.ttl is not None else APP_TTL
                if ttl > 0 and (now - info.last_accessed > ttl):
                    self.router_logger.info(f"TTL expired for '{name}', freeing memory...")
                    info.app = None

    async def _serve_htag_app(self, name: str, info: AppInfo, scope: Scope, receive: Receive, send: Send, new_path: str) -> bool:
        """Handle execution/serving of a specific Htag App."""
        info.last_accessed = time.time()
        mtime = get_app_mtime(info.file)
        
        # Load or Reload if file changed
        if info.app is None or (scope["type"] == "http" and mtime > info.mtime):
            action = "Reloading" if info.app else "Loading"
            self.router_logger.info(f"{action} htag app: {name}")
            app_class = load_htag_app(info.mod_path)
            if app_class:
                # Detect special App attributes
                parano = getattr(app_class, "_parano_", False)
                if parano: self.router_logger.info(f"Parano mode ON for: {name}")
                info.ttl = getattr(app_class, "_ttl_", None)
                if info.ttl is not None: self.router_logger.info(f"Custom TTL for '{name}': {info.ttl}s")
                
                # Wrap htag App class into a Starlette WebApp
                info.app, info.mtime = WebApp(app_class, parano=parano).app, mtime
            else:
                return False

        if info.app:
            # Rewrite paths for the internal htag router
            scope["path"] = new_path
            scope["root_path"] = scope.get("root_path", "") + "/" + name
            await info.app(scope, receive, send)
            return True
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI main entry point."""
        if scope["type"] not in ["http", "websocket"]: return
        if scope["type"] == "http": self._unload_expired_apps()

        path = scope["path"]
        rel_path = path.strip("/")
        
        # Ensure discovery is done at least once
        if not self.apps: self._refresh_discovery()

        exact_target = self.apps_dir / rel_path
        
        # --- PHASE 1: Htag App Matching (Prioritizing longest name) ---
        for name in sorted(self.apps.keys(), key=len, reverse=True):
            if rel_path == name or rel_path.startswith(name + "/"):
                info = self.apps[name]
                if rel_path == name or rel_path == name + "/":
                    # Direct access to the app
                    new_path = path[len("/" + name):] or "/"
                    if await self._serve_htag_app(name, info, scope, receive, send, new_path):
                        return
                else:
                    # Potential file within the app's folder path
                    sub_rel = rel_path[len(name):].lstrip("/")
                    sub_full = info.file.parent / sub_rel
                    
                    # Auto-detect script without extension
                    if not sub_full.is_file() and "." not in sub_full.name:
                        py_attempt = sub_full.with_name(sub_full.name + ".py")
                        if py_attempt.is_file(): sub_full = py_attempt

                    if sub_full.is_file():
                        exact_target = sub_full
                        break # Found a file, move to Phase 2
                    
                    # Not a file? Probably an htag endpoint (/ws, /stream, /event)
                    new_path = path[len("/" + name):] or "/"
                    if await self._serve_htag_app(name, info, scope, receive, send, new_path):
                        return

        # --- PHASE 2: File Handling (Static or Extensionless Scripts) ---
        full_path = exact_target
        if not exact_target.is_file() and not rel_path.endswith(".py") and "." not in rel_path.split("/")[-1]:
            py_attempt = exact_target.with_name(exact_target.name + ".py")
            if py_attempt.is_file(): full_path = py_attempt

        if full_path.is_file():
            if full_path.suffix == ".py":
                # Security: Forbidden to access .py directly (must use extensionless URL)
                if rel_path.endswith(".py"):
                    if scope["type"] == "http": await HTMLResponse("Not found", status_code=404)(scope, receive, send)
                    return
                # Run standalone script
                if scope["type"] == "http":
                    response = await self.script_runner.run(full_path, scope)
                    await response(scope, receive, send)
                return
            elif full_path.suffix != ".pyc":
                # Serve static file (ignores bytecodes)
                if scope["type"] == "http": await FileResponse(str(full_path))(scope, receive, send)
                return
            
            # Blocked file (like .pyc)
            if scope["type"] == "http": await HTMLResponse("Not found", status_code=404)(scope, receive, send)
            return

        # --- PHASE 3: Directory Management & Indexing ---
        if not rel_path or full_path.is_dir():
            # Security: Path traversal check
            if not full_path.resolve().is_relative_to(self.apps_dir):
                if scope["type"] == "http": await HTMLResponse("Forbidden", status_code=403)(scope, receive, send)
                return

            # Refresh disk status for potential new files
            self._refresh_discovery()
            
            # Check if current directory IS a newly discovered app
            for name, info in self.apps.items():
                if rel_path == name or rel_path == name + "/":
                     if await self._serve_htag_app(name, info, scope, receive, send, "/"):
                        return

            if scope["type"] == "http":
                # Canonical trailing slash for directories
                if rel_path and not path.endswith("/"):
                    await HTMLResponse("", status_code=301, headers={"Location": path + "/"})(scope, receive, send)
                    return

                # Option 1: Generate Listing
                if self.auto_index:
                    await HTMLResponse(IndexGenerator.generate(self.apps_dir, self.apps, rel_path))(scope, receive, send)
                    return
                
                # Option 2: Default entrypoints (Prioritized)
                index_html = full_path / "index.html"
                if index_html.is_file():
                    await FileResponse(str(index_html))(scope, receive, send)
                    return

                index_name = f"{rel_path}/index" if rel_path else "index"
                if index_name in self.apps:
                    if await self._serve_htag_app(index_name, self.apps[index_name], scope, receive, send, "/"):
                        return

                index_py = full_path / "index.py"
                if index_py.is_file():
                    response = await self.script_runner.run(index_py, scope)
                    await response(scope, receive, send)
                    return

                await HTMLResponse("No default entrypoint", status_code=400)(scope, receive, send)
            return

        # 404 Fallback
        if scope["type"] == "http":
            self.router_logger.info(f"Path not found: {path}")
            await HTMLResponse("Not found", status_code=404)(scope, receive, send)


if __name__ == "__main__":
    import uvicorn
    # Standalone server configuration (Demo mode)
    logging.basicConfig(
        format="[%(asctime)s] %(levelname)-8s %(name)-15s: %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # Use 'www' subfolder from current script location
    apps_dir = Path(__file__).parent / "www"
    
    # Ensure current directory is in PYTHONPATH for easy imports
    sys.path.insert(0, str(apps_dir.parent))
    
    # Start server with Auto-Index enabled
    app = DynamicHtagApps(apps_dir, auto_index=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)

