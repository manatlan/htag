# pye (Python Everywhere)

`pye` is a dynamic server built on **Starlette** and **htag**, designed to serve static files, standalone Python scripts, and full htag applications seamlessly.

## Core Features

- **Multi-HTAG Apps**: Automatically discovers and routes to multiple htag applications.
- **Standalone Scripts**: Executes `.py` files as scripts and returns their output.
- **Static File Serving**: Serves any other file types as static assets.
- **Hot Reloading**: Detects changes in htag apps and reloads them automatically.
- **TTL Management**: Unloads inactive htag apps after a period of inactivity (default 10 minutes) to save resources.

## How it works

The heart of the server is the `DynamicHtagApps` ASGI middleware. It intercepts requests and decides how to handle them based on the path and file system content.

### Application Discovery

The server performs **Lazy Discovery**: it doesn't scan the directory at startup. Instead, it scans the `www` folder upon the first request or when a directory listing is needed. It looks for:
- Directories containing an `__init__.py` with an `App` class (treated as a package htag app).
- `.py` files containing an `App` class (treated as a file htag app).

### Request Routing Logic

When a request arrives, the server follows this prioritized logic:

1.  **Exact File Match**: If the path points exactly to an existing file (except `__init__.py`):
    -   If it's a `.py` file: Access is **forbidden** if the extension is explicitly in the URL (returns 404). Scripts MUST be accessed without the extension.
    -   Otherwise: Serves it as a static file.
2.  **Extensionless Script Match**: If `/toto` is requested and `/toto.py` exists (and is not an htag app), it executes it as a standalone script.
3.  **HTAG App Match**: If the path starts with an htag app name (e.g., `/myapp/`):
    -   The request is handed over to the `htag.server.WebApp` instance for that app.
4.  **Directory Access**: If the path points to a directory:

#### `auto_index = True` (Default for dev)
-   Generates and serves a dynamic **HTML directory listing**. 
-   **Note**: This takes precedence over any `index.html` or `index.py`.
-   Shows folders, htag apps (with 🚀), scripts (with 🐍, extension hidden), and static files.

#### `auto_index = False` (Production-like)
-   Attempts to find a default entry point in the following order:
    1.  `index.html`: Serves it as a static file if it exists.
    2.  `index.py` (htag app): Loads and serves it as an htag app.
    3.  `index.py` (script): Executes it as a script and serves the output.
-   If none are found, returns `400 No default entrypoint`.

### Standalone Script Execution
Scripts are executed in a subprocess using the current Python interpreter. Common CGI-like environment variables (`QUERY_STRING`, `REQUEST_METHOD`, `PATH_INFO`) are provided to the script.

### HTAG App Configuration

HTAG apps can customize their behavior by defining specific class attributes:

- **Parano Mode (`_parano_`)**: If `_parano_ = True` is defined in the `App` class, all communication for this specific app (WebSockets and HTTP fallback) will be obfuscated.
- **Custom TTL (`_ttl_`)**: If `_ttl_ = <seconds>` is defined, it overrides the server's default TTL for this application instance.
    - Set `_ttl_ = 0` to make the application **persistent** (it will never be unloaded).

Example:
```python
from htag import Tag

class App(Tag.App):
    _parano_ = True  # Enable obfuscation
    _ttl_ = 3600    # Keep in memory for 1 hour
    
    def init(self):
        self <= "Hello Secure & Persistent App"
```

### Auto-Reload
If the source file (or any `.py` file in a package app) is modified, the app is reloaded on the next request.

### TTL (Time To Live)
Apps are kept in memory but are automatically discarded if not accessed for 10 minutes (default). This behavior is individual per application if `_ttl_` is specified.
