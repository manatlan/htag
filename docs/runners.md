# Runners

Runners are responsible for hosting your `App` and launching the interface.

## Web Deployment (Starlette Integration)

For web-based deployment, we recommend integrating your `htag` application directly into a **Starlette** (or FastAPI) server. This provides the most flexibility and follows standard Python web practices.

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
    - Seamlessly mix standard HTML/API routes with reactive `htag` components.
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

## Resiliency & Transport Fallback

`htag` implements a robust **3-level transport fallback** mechanism to ensure connectivity across all network environments:

1.  **Level 1: WebSocket** (Primary): Full bidirectional communication.
2.  **Level 2: SSE (Server-Sent Events)**: Unidirectional push from server; used if WebSockets are blocked by proxies.
3.  **Level 3: Pure HTTP**: Last-resort synchronous POST communication. The server buffers UI updates in a session-specific queue and returns them directly in the next event response.

This ensures your application remains functional even behind the strictest corporate firewalls or unstable mobile connections.

## Forcing Protocol via Cookie (`htag_mode`)

In some restricted network environments (e.g., corporate proxies), WebSockets or SSE might be technically "available" but extremely slow to time out, causing a long delay before falling back to a working mode.

`htag` supports forcing a specific protocol via the `htag_mode` cookie, bypassing the standard auto-detection:

- **`htag_mode=http`**: Forces the application into pure HTTP mode (Level 3) immediately.
- **`htag_mode=sse`**: Forces the application into SSE mode (Level 2).
- **(Absent)**: Default behavior (WebSocket -> SSE -> HTTP).

**Usage**:
You can set this cookie manually in the browser console:
`document.cookie="htag_mode=http;path=/"`
Refresh the page to apply the change.

## Session & Cookie Path

When using `WebApp`, `htag` manages sessions using a `htag_sid` cookie. 
- **Root Path**: The cookie is automatically set with `path="/"`. This ensures session continuity and CSRF validation even if your application uses multiple sub-paths or is mounted at a non-root location.
- **CSRF Protection**: Every event request is validated against a session-unique CSRF token passed in the `X-HTAG-TOKEN` header.

## Development & Hot-Reload (DX)

For an improved Developer Experience (DX), you can pass `reload=True` to the runner during development:

```python
if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(MyApp).run(reload=True) 
```

When `reload=True` is provided:
1. **Zero-Config File Watcher**: `htag` spawns a master process that watches all `.py` files in your current directory recursively.
2. **Auto-Restart**: When you save a file, the Python ASGI backend is instantly terminated and restarted with your new code.
3. **Seamless Browser Refresh**: The UI frontend stays open. It will realize the backend went offline, automatically poll for reconnection, and gracefully refresh the window once the new backend is up.

## Ephemeral Ports (`port=0`)

When developing locally or running automated tests, you may run into "Address already in use" errors if a previous process didn't shut down correctly or if multiple apps are running.

You can pass `port=0` to any runner's `run()` method. `htag` will:
1.  Ask the Operating System for an available random port.
2.  Reserve it and ensure it's used by the underlying `uvicorn` server.
3.  Automatically open the browser (or Chrome window) on that specific port.
4.  If `reload=True` is used, the port remains consistent across all auto-restarts.

```python
if __name__ == "__main__":
    from htag import ChromeApp
    # Automatically picks a free port
    ChromeApp(MyApp).run(port=0) 
```

---

[← Events](events.md) | [Next: Advanced →](advanced.md)
