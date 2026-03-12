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

# Configure logging
logging.basicConfig(
    format="[%(asctime)s] %(levelname)-8s %(name)-15s: %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pye")

APP_TTL = 10 * 60  # 10 minutes
AUTO_INDEX = False  # Set to False to disable directory index listing


def get_app_mtime(p: Path) -> float:
    """Retrieve the maximum modification time for an htag application."""
    if p.is_file():
        if p.name == "__init__.py":
            try:
                mtime = max(
                    (f.stat().st_mtime for f in p.parent.rglob("*.py")),
                    default=p.stat().st_mtime,
                )
                return mtime
            except Exception:
                pass
        return p.stat().st_mtime
    return 0.0


def load_htag_app(mod_path: str) -> Type[Tag.App] | None:
    """Helper to load/reload a module and extract the htag App class."""
    try:
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


@dataclass
class AppInfo:
    """Metadata for a discovered htag application."""

    app: Starlette | None
    file: Path
    mtime: float
    mod_path: str
    last_accessed: float


class AppDiscoverer:
    """Handles discovery of htag applications in a directory."""

    def __init__(self, apps_dir: Path):
        self.apps_dir = apps_dir
        self.logger = logger.getChild("discovery")

    def discover(self) -> dict[str, AppInfo]:
        """Scan directory and return mapping of name -> AppInfo."""
        found_apps: dict[str, AppInfo] = {}
        self.logger.info(f"Scanning directory: {self.apps_dir}")

        def crawl(current_dir: Path, rel_root: str = "") -> None:
            for p in current_dir.iterdir():
                if p.name == "__pycache__":
                    continue

                rel_path = f"{rel_root}/{p.name}" if rel_root else p.name

                if p.is_dir():
                    init_file = p / "__init__.py"
                    if init_file.exists():
                        mod_path = f"www.{rel_path.replace('/', '.')}"
                        app_class = load_htag_app(mod_path)
                        if app_class:
                            self.logger.info(f"Discovered package app: {rel_path} ({mod_path})")
                            found_apps[rel_path] = AppInfo(
                                app=WebApp(app_class).app,
                                file=init_file,
                                mtime=get_app_mtime(init_file),
                                mod_path=mod_path,
                                last_accessed=time.time(),
                            )
                            continue
                    crawl(p, rel_path)
                elif p.is_file() and p.name.endswith(".py") and p.name != "__init__.py":
                    app_name = rel_path[:-3]
                    mod_path = f"www.{app_name.replace('/', '.')}"
                    app_class = load_htag_app(mod_path)
                    if app_class:
                        self.logger.info(f"Discovered file app: {app_name} ({mod_path})")
                        found_apps[app_name] = AppInfo(
                            app=WebApp(app_class).app,
                            file=p,
                            mtime=get_app_mtime(p),
                            mod_path=mod_path,
                            last_accessed=time.time(),
                        )

        if self.apps_dir.exists() and self.apps_dir.is_dir():
            crawl(self.apps_dir)
        self.logger.info(f"Discovery complete. Found {len(found_apps)} apps.")
        return found_apps


class IndexGenerator:
    """Generates HTML directory listings."""

    @staticmethod
    def generate(apps_dir: Path, apps: dict[str, AppInfo], prefix: str = "") -> str:
        target_dir = apps_dir / prefix
        if not target_dir.is_dir():
            return ""

        items: list[str] = []
        if prefix:
            parent = str(Path(prefix).parent)
            parent_link = f"/{parent}/" if parent != "." else "/"
            items.append(f'<li>📁 <a href="{parent_link}">.. (Parent Directory)</a></li>')

        folders, htag_apps, scripts, statics = [], [], [], []
        for p in sorted(target_dir.iterdir()):
            if p.name == "__pycache__" or p.name.startswith("."):
                continue
            
            rel_item = f"{prefix}/{p.name}" if prefix else p.name
            if p.is_dir():
                if (p / "__init__.py").is_file() and rel_item in apps:
                    htag_apps.append(p.name)
                else:
                    folders.append(p.name)
            else:
                if p.name == "__init__.py": continue
                if p.name.endswith(".py"):
                    if rel_item[:-3] in apps: htag_apps.append(p.name[:-3])
                    else: scripts.append(p.name)
                else:
                    statics.append(p.name)

        def link(name, is_dir=False):
            return f"/{prefix}/{name}" + ("/" if is_dir else "") if prefix else f"/{name}" + ("/" if is_dir else "")

        for f in sorted(folders): items.append(f'<li>📁 <a href="{link(f, True)}">{f}/</a></li>')
        for a in sorted(htag_apps): items.append(f'<li>🚀 <a href="{link(a, True)}">{a}</a> <small style="color:#888">(htag App)</small></li>')
        for s in sorted(scripts): items.append(f'<li>🐍 <a href="{link(s)}">{s}</a> <small style="color:#888">(Script)</small></li>')
        for s in sorted(statics): items.append(f'<li>📄 <a href="{link(s)}">{s}</a></li>')

        title = f"Index of {prefix}/" if prefix else "Root Index"
        content = f'<ul style="list-style-type: none; padding-left: 10px;">{"".join(items)}</ul>' if items else "<p>No entries found.</p>"
        return f"<html><head><title>{title}</title><style>body {{ font-family: sans-serif; }} li {{ margin: 6px 0; }} a {{ text-decoration: none; color: #0366d6; font-size: 16px; }} a:hover {{ text-decoration: underline; }}</style></head><body><h1>{title}</h1>{content}</body></html>"


class ScriptRunner:
    """Handles execution of standalone Python scripts."""

    @staticmethod
    async def run(full_path: Path, scope: Scope) -> HTMLResponse:
        """Executes a Python script and returns its output as an HTMLResponse."""
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
                script_logger.warning(f"Script '{script_name}' produced stderr: {stderr.decode('utf-8', errors='replace')}")

            if proc.returncode == 0:
                script_logger.info(f"Script '{script_name}' finished successfully")
                return HTMLResponse(stdout.decode("utf-8", errors="replace"))
            
            script_logger.error(f"Script '{script_name}' failed with return code {proc.returncode}")
            return HTMLResponse(
                f"<html><body><h1>Script Error</h1><pre>{stderr.decode('utf-8', errors='replace')}</pre></body></html>",
                status_code=500
            )
        except asyncio.TimeoutError:
            script_logger.error(f"Script '{script_name}' timed out after 10s")
            return HTMLResponse("<html><body><h1>Script Timeout</h1></body></html>", status_code=504)
        except Exception as e:
            script_logger.error(f"Failed to execute script '{script_name}': {e}", exc_info=True)
            return HTMLResponse(f"Execution failed: {e}", status_code=500)


class DynamicHtagApps:
    """Dynamic Starlette router for htag apps, scripts, and static files."""

    def __init__(self, apps_dir: str | Path):
        self.router_logger = logger.getChild("router")
        self.apps_dir = Path(apps_dir).resolve()
        parent_dir = str(self.apps_dir.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        self.discoverer = AppDiscoverer(self.apps_dir)
        self.apps = self.discoverer.discover()

    def _unload_expired_apps(self):
        now = time.time()
        for name, info in list(self.apps.items()):
            if info.app is not None and (now - info.last_accessed > APP_TTL):
                self.router_logger.info(f"TTL expired for htag app '{name}', unloading...")
                info.app = None

    async def _serve_htag_app(self, name: str, info: AppInfo, scope: Scope, receive: Receive, send: Send, new_path: str) -> bool:
        """Loads and serves an htag application."""
        info.last_accessed = time.time()
        mtime = get_app_mtime(info.file)
        
        if info.app is None or (scope["type"] == "http" and mtime > info.mtime):
            action = "Reloading" if info.app else "Loading"
            self.router_logger.info(f"{action} htag app: {name}")
            app_class = load_htag_app(info.mod_path)
            if app_class:
                info.app, info.mtime = WebApp(app_class).app, mtime
            else:
                return False

        if info.app:
            scope["path"] = new_path
            scope["root_path"] = scope.get("root_path", "") + "/" + name
            await info.app(scope, receive, send)
            return True
        return False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]: return
        if scope["type"] == "http": self._unload_expired_apps()

        path = scope["path"]
        rel_path = path.strip("/")
        
        # 1. Htag App?
        exact_target = self.apps_dir / rel_path
        if not (exact_target.exists() and exact_target.is_file() and exact_target.name != "__init__.py"):
            for name in sorted(self.apps.keys(), key=len, reverse=True):
                if rel_path == name or rel_path.startswith(name + "/"):
                    info = self.apps[name]
                    new_path = path[len("/" + name):] or "/"
                    if await self._serve_htag_app(name, info, scope, receive, send, new_path):
                        return

        # 2. Directory or Index
        full_path = self.apps_dir / rel_path
        if not full_path.resolve().is_relative_to(self.apps_dir):
            if scope["type"] == "http":
                self.router_logger.warning(f"Forbidden access attempt: {path}")
                await HTMLResponse("Forbidden", status_code=403)(scope, receive, send)
            return

        if not rel_path or full_path.is_dir():
            if scope["type"] == "http":
                if rel_path and not path.endswith("/"):
                    await HTMLResponse("", status_code=301, headers={"Location": path + "/"})(scope, receive, send)
                else:
                    if AUTO_INDEX:
                        self.router_logger.info(f"Serving directory index: {path}")
                        await HTMLResponse(IndexGenerator.generate(self.apps_dir, self.apps, rel_path))(scope, receive, send)
                    else:
                        index_name = f"{rel_path}/index" if rel_path else "index"
                        if index_name in self.apps:
                            if await self._serve_htag_app(index_name, self.apps[index_name], scope, receive, send, "/"):
                                return

                        index_file = full_path / "index.py"
                        if index_file.is_file():
                            self.router_logger.info(f"Running default index script: {index_file}")
                            response = await ScriptRunner.run(index_file, scope)
                            await response(scope, receive, send)
                            return

                        self.router_logger.warning(f"No entrypoint found and AUTO_INDEX is False: {path}")
                        await HTMLResponse("No default entrypoint", status_code=400)(scope, receive, send)
            return

        # 3. Static or Script
        if not full_path.is_file() and "." not in full_path.name:
            py_attempt = full_path.with_name(full_path.name + ".py")
            if py_attempt.is_file(): full_path = py_attempt

        if full_path.is_file():
            if full_path.suffix == ".py":
                if scope["type"] == "http":
                    response = await ScriptRunner.run(full_path, scope)
                    await response(scope, receive, send)
            elif full_path.suffix == ".pyc":
                if scope["type"] == "http":
                    self.router_logger.warning(f"Attempt to access bytecode: {path}")
                    await HTMLResponse("Forbidden", status_code=403)(scope, receive, send)
            else:
                if scope["type"] == "http":
                    self.router_logger.info(f"Serving static file: {path}")
                    await FileResponse(str(full_path))(scope, receive, send)
            return

        if scope["type"] == "http":
            self.router_logger.info(f"Path not found: {path}")
            await HTMLResponse("Not found", status_code=404)(scope, receive, send)


app = DynamicHtagApps(Path(__file__).parent / "www")

if __name__ == "__main__":
    import uvicorn
    AUTO_INDEX = True  # Enable indexing for demo
    uvicorn.run(app, host="0.0.0.0", port=8000)

