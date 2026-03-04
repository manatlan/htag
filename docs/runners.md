# Runners

Runners are responsible for hosting your `App` and launching the interface.

## Web Deployment (Starlette Integration)

For web-based deployment, we recommend integrating your `htag2` application directly into a **Starlette** (or FastAPI) server. This provides the most flexibility and follows standard Python web practices.

```python
from htag import Tag
from starlette.applications import Starlette
import uvicorn

class MyApp(Tag.App):
    def init(self):
        self <= Tag.h1("I am a web app")

# 1. Create your main Starlette/FastAPI app
app = Starlette(debug=False)  # Starlette's own debug mode

# 2. Wrap your htag app in a WebApp runner
from htag import WebApp
# Wrap your htag App in a WebApp
htag_app = WebApp(MyApp)

# Mount or include routes
app.mount("/htag", htag_app.app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- **Advantages**: 
    - Full control over routes, middleware, and documentation.
    - Seamlessly mix standard HTML/API routes with reactive `htag2` components.
    - Support for subpath mounting (e.g., `app.mount("/app", ...)`).
    - Built-in `parano=True` mode for payload obfuscation (dynamic XOR cipher) to protect traffic against simple MITM proxies.

## Desktop Deployment (ChromeApp)

`ChromeApp` is the primary runner for local desktop usage. It attempts to launch a clean desktop-like Kiosk window via Chromium/Chrome binaries.

```python
from htag import ChromeApp, Tag

class MyApp(Tag.App):
    pass

if __name__ == "__main__":
    # debug=True (default) enables browser-side error reporting
    ChromeApp(MyApp, width=600, height=800, debug=True).run()
```

- **Features**:
    - Clean UI without URL bars or browser tabs.
    - Automatic cleanup of temporary browser profiles.
    - **Smart Exit**: Automatically shuts down the Python server when the window is closed.

## Development & Hot-Reload (DX)

For an improved Developer Experience (DX), you can pass `reload=True` to the runner during development:

```python
if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(MyApp).run(reload=True) 
```

When `reload=True` is provided:
1. **Zero-Config File Watcher**: `htag2` spawns a master process that watches all `.py` files in your current directory recursively.
2. **Auto-Restart**: When you save a file, the Python ASGI backend is instantly terminated and restarted with your new code.
3. **Seamless Browser Refresh**: The UI frontend stays open. It will realize the backend went offline, automatically poll for reconnection, and gracefully refresh the window once the new backend is up.

---

[← Events](events.md) | [Next: Advanced →](advanced.md)
