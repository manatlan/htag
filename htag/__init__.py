from .core import prevent, stop, State, current_request
from .tag import Tag
from .runner import AppRunner as App
from .web import WebApp
from .runners import ChromeApp, PyScript

import logging

# Library best practice: attach NullHandler so apps that don't configure
# logging won't see "No handler found" warnings.
logging.getLogger("htag").addHandler(logging.NullHandler())

__all__ = [
    "Tag",  # the main thing
    "State",    # State management
    "WebApp",   # the ASGI runner

    # Specialize runners
    "ChromeApp",
    "PyScript",

    # events decorator
    "prevent",
    "stop",

]
