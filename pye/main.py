import os
import sys
import importlib
import inspect
import ast
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from htag.server import WebApp # Renamed from WebServer
from htag import Tag

class DynamicHtagApps:
    def __init__(self, apps_dir: str):
        self.apps_dir = os.path.abspath(apps_dir)
        self.apps_cache = {} # path -> (mtime, starlette_app)
        
    async def __call__(self, scope, receive, send):
        if scope["type"] not in ["http", "websocket"]:
            return

        path = scope["path"]
        
        # Example: path "/toto/" or "/toto/ws"
        parts = path.strip("/").split("/")
        app_name = parts[0]
        
        if not app_name:
            # Root path: list available apps
            if scope["type"] == "http":
                apps = []
                for entry in os.listdir(self.apps_dir):
                    filename = None
                    if entry.endswith(".py") and entry != "__init__.py":
                        filename = os.path.join(self.apps_dir, entry)
                        app_name = entry.replace(".py", "")
                    elif os.path.isdir(os.path.join(self.apps_dir, entry)):
                        init_file = os.path.join(self.apps_dir, entry, "__init__.py")
                        if os.path.exists(init_file):
                            filename = init_file
                            app_name = entry
                    
                    # Check if 'app' is defined in the file using AST to avoid importing
                    if filename:
                        try:
                            with open(filename, "r", encoding="utf-8") as f:
                                tree = ast.parse(f.read(), filename=filename)
                            has_app = any(
                                isinstance(node, ast.Assign) and 
                                any(isinstance(t, ast.Name) and t.id == 'app' for t in node.targets)
                                for node in ast.walk(tree)
                            )
                            if has_app:
                                apps.append(app_name)
                        except Exception:
                            pass
                
                apps.sort()
                links = "".join([f'<li><a href="/{a}/">{a}</a></li>' for a in apps])
                html = f"<html><body><h1>Dynamic Apps</h1><ul>{links}</ul></body></html>"
                response = HTMLResponse(html)
                await response(scope, receive, send)
            return

        py_file = os.path.join(self.apps_dir, f"{app_name}.py")
        is_pkg = False
        
        if not os.path.exists(py_file):
            # Check if it's a package
            pkg_dir = os.path.join(self.apps_dir, app_name)
            if os.path.isdir(pkg_dir):
                py_file = os.path.join(pkg_dir, "__init__.py")
                if os.path.exists(py_file):
                    is_pkg = True
                else:
                    if scope["type"] == "http":
                        response = HTMLResponse(f"Directory {app_name} is not a Python package (missing __init__.py)", status_code=404)
                        await response(scope, receive, send)
                    return
            else:
                if scope["type"] == "http":
                    response = HTMLResponse("App not found", status_code=404)
                    await response(scope, receive, send)
                return

        mtime = os.stat(py_file).st_mtime
        
        if app_name not in self.apps_cache or self.apps_cache[app_name][0] < mtime:
            # The apps are in the 'www' directory relative to this file
            mod_name = f"www.{app_name}"
            
            parent_dir = os.path.dirname(os.path.abspath(__file__))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                
            if mod_name in sys.modules:
                mod = importlib.reload(sys.modules[mod_name])
            else:
                mod = importlib.import_module(mod_name)
                
            app_class = getattr(mod, "app", None)
                    
            if not app_class or not (isinstance(app_class, type) and issubclass(app_class, Tag.App)):
                if scope["type"] == "http":
                    response = HTMLResponse("No 'app' variable defining a Tag.App found in module", status_code=404)
                    await response(scope, receive, send)
                return
                
            # Create the WebApp for this app
            wa = WebApp(app_class)
            self.apps_cache[app_name] = (mtime, wa.app)
            print(f"Loaded/Reloaded {app_name} from {py_file}")

        _, sub_app = self.apps_cache[app_name]
        
        # Adjust scope for the sub-app
        app_path = "/" + app_name
        path = scope.get("path", "")
        root_path = scope.get("root_path", "")
        
        if path.startswith(app_path):
            scope["path"] = path[len(app_path):]
            if scope["path"] == "":
                 scope["path"] = "/"
            scope["root_path"] = root_path + app_path
            
        await sub_app(scope, receive, send)

app = DynamicHtagApps(os.path.join(os.path.dirname(__file__), "www"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
