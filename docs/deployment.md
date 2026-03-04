# Production Deployment

While runners are great for development and desktop apps, `htag` applications are fully compatible with production-grade web servers.

## Starlette Integration

Every `Tag.App` in `htag` exposes an underlying **Starlette** instance through its `.app` property. This allows you to deploy your application using standard tools like `uvicorn` or `gunicorn`.

### Basic Production Entrypoint

```python
# app.py
from htag import Tag

class MyApp(Tag.App):
    def init(self):
        self <= Tag.h1("Production App")

# Create the WebApp runner (production: debug=False)
from htag.server import WebApp
app = WebApp(MyApp, debug=False).app
```

You can now run this with `uvicorn`:

```bash
uvicorn app:app --host 0.0.0.0 --port 80
```

### Security Options (Parano Mode)

When exposing your application on the internet, you can use the `parano=True` argument when initializing your `WebApp`. This enables **Parano Mode**, which obfuscates all JSON payloads exchanged between the frontend and backend (over WebSockets and HTTP fallbacks) using a dynamic XOR cipher. This makes your network traffic unreadable to simple Man-In-The-Middle (MITM) proxies without needing complex cryptography libraries.

```python
# Create the WebApp runner with payload obfuscation
from htag.server import WebApp
app = WebApp(MyApp, debug=False, parano=True).app
```

## Embedding htag in existing Starlette/FastAPI apps

Since `htag` uses a `WebApp` wrapper, you can also mount it as a sub-application or include its routes in a larger Starlette or FastAPI project.

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from htag.server import WebApp
from my_htag_app import MyApp

main_app = Starlette()

# Wrap your htag App in a WebApp
htag_app = WebApp(MyApp)

# Mount or include routes
main_app.mount("/htag", htag_app.app)

@main_app.route("/health")
def health(request):
    return JSONResponse({"status": "ok"})
```

## Performance & Scalability

- **WebSockets**: Ensure your production load balancer (like Nginx or Traefik) is configured to handle WebSocket connections properly.
- **Workers**: Since `htag` maintains session state in memory (by default), you should ideally use **sticky sessions** if you scale to multiple worker processes or containers.
- **Memory**: Each active session consumes a small amount of memory on the server. Monitor your memory usage if you expect thousands of concurrent users.

---

[← Runners](runners.md) | [Home](index.md)
