from .core import prevent, stop, State, current_request
from .tag import Tag
from .runner import AppRunner as App
from .web import WebApp
from .router import Router
from .runners import ChromeApp, PyScript

import logging
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("htag")
except PackageNotFoundError:
    # package is not installed
    __version__ = "unknown"

# Library best practice: attach NullHandler so apps that don't configure
# logging won't see "No handler found" warnings.
logging.getLogger("htag").addHandler(logging.NullHandler())

__all__ = [
    "__version__",
    "Tag",  # the main thing
    "State",    # State management
    "Router",   # SPA hash-based router
    "WebApp",   # the ASGI runner

    # Specialized runners
    "ChromeApp",
    "PyScript",

    # events decorator
    "prevent",
    "stop",

]


