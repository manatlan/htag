# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

# mono instance
from .browserhttp import BrowserHTTP

try:
    # mono instance
    from .browserstarlettehttp import BrowserStarletteHTTP
    from .browserstarlettews import BrowserStarletteWS

    # multi instance
    from .webhttp import WebHTTP

except ImportError:
    print("You should install 'starlette' & 'uvicorn' for this htag runner")

try:
    # mono instance (juste one pywebview ;-)
    from .pywebview import PyWebWiew
except ImportError:
    print("You should install 'pywebview' for this htag runner")

try:
    # mono instance (only ! htag limitation)
    from .guyapp import GuyApp
except ImportError:
    print("You should install 'guy' for this htag runner")


