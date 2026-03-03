import asyncio
import importlib
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, FileResponse
from starlette.types import Receive, Scope, Send

from htag import Tag
from htag.server import WebApp


def get_app_mtime(p: Path) -> float:
    """
    Retrieve the maximum modification time for an htag application.

    If the path is an '__init__.py', it recursively checks all '.py' files
    in the parent directory to detect any changes in the app's components.

    Args:
        p (Path): The file path to check.

    Returns:
        float: The highest modification timestamp found.
    """
    if p.is_file():
        if p.name == "__init__.py":
            try:
                return max(
                    (f.stat().st_mtime for f in p.parent.rglob("*.py")),
                    default=p.stat().st_mtime,
                )
            except Exception:
                pass
        return p.stat().st_mtime
    return 0.0


@dataclass
class AppInfo:
    """
    Data class storing metadata for a discovered htag application.
    """

    app: Starlette
    file: Path
    mtime: float
    mod_path: str


class DynamicHtagApps:
    """
    A dynamic Starlette application router that automatically discovers, serves,
    and hot-reloads htag applications, static files, and standalone Python scripts
    from a specified directory.
    """

    def __init__(self, apps_dir: str | Path):
        """
        Initialize the DynamicHtagApps router.

        Args:
            apps_dir (str | Path): The root directory containing apps and files to serve.
        """
        self.apps_dir: Path = Path(apps_dir).resolve()
        self.apps: dict[str, AppInfo] = {}  # name -> AppInfo

        parent_dir: str = str(Path(__file__).resolve().parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        self._discover_apps()

    def _discover_apps(self) -> None:
        """
        Scan the apps_dir to discover htag applications and cache their Starlette instances.

        It looks for `.py` files containing an `app` class extending `Tag.App`, or
        directories containing an `__init__.py` with the same.
        """
        self.apps.clear()

        if not self.apps_dir.exists() or not self.apps_dir.is_dir():
            return

        def crawl(current_dir: Path, rel_root: str = "") -> None:
            for p in current_dir.iterdir():
                if p.name == "__pycache__":
                    continue

                rel_path: str = f"{rel_root}/{p.name}" if rel_root else p.name

                if p.is_dir():
                    init_file = p / "__init__.py"
                    if init_file.exists():
                        # It's an htag package
                        mod_path: str = f"www.{rel_path.replace('/', '.')}"
                        try:
                            mod = (
                                importlib.reload(sys.modules[mod_path])
                                if mod_path in sys.modules
                                else importlib.import_module(mod_path)
                            )
                            app_class = getattr(mod, "app", None)
                            if (
                                app_class
                                and isinstance(app_class, type)
                                and issubclass(app_class, Tag.App)
                            ):
                                wa = WebApp(app_class)
                                self.apps[rel_path] = AppInfo(
                                    app=wa.app,
                                    file=init_file,
                                    mtime=get_app_mtime(init_file),
                                    mod_path=mod_path,
                                )
                                continue  # Don't descend further into an app package
                        except Exception as e:
                            print(f"WARNING: Discovery failed for {mod_path}: {e}")
                            pass

                    # Not a package, or package failed to load, crawl inside
                    crawl(p, rel_path)

                elif p.is_file():
                    if p.name in ("__init__.py",) or p.name.endswith(".pyc"):
                        continue

                    if p.name.endswith(".py"):
                        app_name: str = rel_path[:-3]
                        mod_path = f"www.{app_name.replace('/', '.')}"
                        try:
                            mod = (
                                importlib.reload(sys.modules[mod_path])
                                if mod_path in sys.modules
                                else importlib.import_module(mod_path)
                            )
                            app_class = getattr(mod, "app", None)
                            if (
                                app_class
                                and isinstance(app_class, type)
                                and issubclass(app_class, Tag.App)
                            ):
                                wa = WebApp(app_class)
                                self.apps[app_name] = AppInfo(
                                    app=wa.app,
                                    file=p,
                                    mtime=get_app_mtime(p),
                                    mod_path=mod_path,
                                )
                        except Exception as e:
                            print(f"WARNING: Discovery failed for {mod_path}: {e}")
                            pass

        crawl(self.apps_dir)

    def _generate_index(self, prefix: str = "") -> str:
        """
        Generate an HTML index of the contents of the given directory prefix.

        Args:
            prefix (str): The relative path from apps_dir to list.

        Returns:
            str: An HTML string representing the directory listing.
        """
        target_dir: Path = self.apps_dir / prefix
        if not target_dir.is_dir():
            return ""

        folders: list[str] = []
        apps: list[str] = []
        scripts: list[str] = []
        statics: list[str] = []

        for p in target_dir.iterdir():
            name: str = p.name
            if name == "__pycache__" or name.startswith("."):
                continue

            if p.is_dir():
                rel_item: str = f"{prefix}/{name}" if prefix else name
                if (p / "__init__.py").is_file() and rel_item in self.apps:
                    apps.append(name)
                else:
                    folders.append(name)
            elif p.is_file():
                if name == "__init__.py" or name.endswith(".pyc"):
                    continue

                rel_item = f"{prefix}/{name}" if prefix else name
                if name.endswith(".py"):
                    app_name: str = rel_item[:-3]
                    if app_name in self.apps:
                        apps.append(name[:-3])
                    else:
                        scripts.append(name)
                else:
                    statics.append(name)

        items: list[str] = []
        if prefix:
            parent: str = "/".join(prefix.split("/")[:-1])
            parent_link: str = f"/{parent}/" if parent else "/"
            items.append(
                f'<li>📁 <a href="{parent_link}">.. (Parent Directory)</a></li>'
            )

        def make_link(name: str, is_dir: bool = False) -> str:
            base: str = f"/{prefix}/{name}" if prefix else f"/{name}"
            return base + "/" if is_dir else base

        for f in sorted(folders):
            items.append(f'<li>📁 <a href="{make_link(f, True)}">{f}/</a></li>')

        for a in sorted(apps):
            items.append(
                f'<li>🚀 <a href="{make_link(a, True)}">{a}</a> <small style="color:#888">(htag App)</small></li>'
            )

        for s in sorted(scripts):
            items.append(
                f'<li>🐍 <a href="{make_link(s)}">{s}</a> <small style="color:#888">(Script)</small></li>'
            )

        for s in sorted(statics):
            items.append(f'<li>📄 <a href="{make_link(s)}">{s}</a></li>')

        content: str = (
            f'<ul style="list-style-type: none; padding-left: 10px;">{"".join(items)}</ul>'
            if items
            else "<p>No entries found.</p>"
        )
        title: str = f"Index of {prefix}/" if prefix else "Root Index"
        return f"<html><head><title>{title}</title><style>body {{ font-family: sans-serif; }} li {{ margin: 6px 0; }} a {{ text-decoration: none; color: #0366d6; font-size: 16px; }} a:hover {{ text-decoration: underline; }}</style></head><body><h1>{title}</h1>{content}</body></html>"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        ASGI application callable. Routes incoming requests to htag apps, scripts, static files, or indexes.

        Args:
            scope (Scope): ASGI scope dictionary.
            receive (Receive): ASGI receive callable.
            send (Send): ASGI send callable.
        """
        if scope["type"] not in ["http", "websocket"]:
            return

        path: str = scope["path"]
        rel_path: str = path.strip("/")

        # 1. Htag App?
        # Try finding the longest matching app prefix
        matching_app: Starlette | None = None
        app_path: str = ""

        # Security/Vampirization check: if it's an exact file (not __init__.py), don't match it as an app route
        # This allows serving static files inside app directories
        exact_target: Path = self.apps_dir / rel_path
        is_exact_file: bool = (
            exact_target.exists()
            and exact_target.is_file()
            and exact_target.name != "__init__.py"
        )

        if not is_exact_file:
            # Sort keys by length descending to find the most specific match
            for name in sorted(self.apps.keys(), key=len, reverse=True):
                if rel_path == name or rel_path.startswith(name + "/"):
                    app_info: AppInfo = self.apps[name]

                    # Check for source file modifications ONLY on http requests (avoid reloading during websocket)
                    try:
                        if scope["type"] == "http":
                            current_mtime: float = get_app_mtime(app_info.file)
                            if current_mtime > app_info.mtime:
                                print(f"INFO: Auto-reloading htag app '{name}'...")
                                mod = importlib.reload(sys.modules[app_info.mod_path])
                                app_class = getattr(mod, "app", None)
                                if (
                                    app_class
                                    and isinstance(app_class, type)
                                    and issubclass(app_class, Tag.App)
                                ):
                                    wa = WebApp(app_class)
                                    app_info.app = wa.app
                                    app_info.mtime = current_mtime
                    except Exception as e:
                        print(f"WARNING: Failed to auto-reload '{name}': {e}")

                    matching_app = app_info.app
                    app_path = "/" + name
                    break

        if matching_app:
            # Adjust scope for the sub-app
            root_path: str = scope.get("root_path", "")
            scope["path"] = path[len(app_path) :]
            if scope["path"] == "":
                scope["path"] = "/"
            scope["root_path"] = root_path + app_path

            await matching_app(scope, receive, send)
            return

        # 2. Root index or Directory index
        full_path: Path = self.apps_dir / rel_path

        # Security: Prevent directory traversal
        if not full_path.resolve().is_relative_to(self.apps_dir):
            if scope["type"] == "http":
                await HTMLResponse("Forbidden", status_code=403)(scope, receive, send)
            return

        if not rel_path or full_path.is_dir():
            if scope["type"] == "http":
                # Ensure trailing slash for directory indexing to keep links working
                if rel_path and not path.endswith("/"):
                    await HTMLResponse(
                        "", status_code=301, headers={"Location": path + "/"}
                    )(scope, receive, send)
                    return

                index_html: str = self._generate_index(rel_path)
                await HTMLResponse(index_html)(scope, receive, send)
            return

        # 3. Static file or Python script?
        # Try appending .py if not found and not clearly a file extension
        if not full_path.is_file() and "." not in Path(rel_path).name:
            py_attempt: Path = full_path.with_name(full_path.name + ".py")
            if py_attempt.is_file():
                full_path = py_attempt

        if full_path.is_file():
            if full_path.suffix == ".py":
                # Always execute, never download
                try:
                    env: dict[str, str] = os.environ.copy()
                    if scope["type"] == "http":
                        env["QUERY_STRING"] = scope.get("query_string", b"").decode(
                            "utf-8", "ignore"
                        )
                        env["REQUEST_METHOD"] = scope.get("method", "GET")
                        env["PATH_INFO"] = path

                    proc = await asyncio.create_subprocess_exec(
                        sys.executable,
                        str(full_path),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                    )
                    try:
                        stdout, stderr = await asyncio.wait_for(
                            proc.communicate(), timeout=10.0
                        )
                        if proc.returncode == 0:
                            response = HTMLResponse(
                                stdout.decode("utf-8", errors="replace")
                            )
                        else:
                            response = HTMLResponse(
                                f"<html><body><h1>Script Error</h1><pre>{stderr.decode('utf-8', errors='replace')}</pre></body></html>",
                                status_code=500,
                            )
                    except asyncio.TimeoutError:
                        proc.kill()
                        response = HTMLResponse(
                            "<html><body><h1>Script Timeout</h1><p>The script took too long to execute.</p></body></html>",
                            status_code=504,
                        )
                except Exception as e:
                    response = HTMLResponse(f"Execution failed: {e}", status_code=500)

                if scope["type"] == "http":
                    await response(scope, receive, send)

            elif full_path.suffix == ".pyc":
                if scope["type"] == "http":
                    await HTMLResponse("Forbidden", status_code=403)(
                        scope, receive, send
                    )
            else:
                if scope["type"] == "http":
                    await FileResponse(str(full_path))(scope, receive, send)
            return

        if scope["type"] == "http":
            await HTMLResponse("App or file not found", status_code=404)(
                scope, receive, send
            )


app = DynamicHtagApps(Path(__file__).parent / "www")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
