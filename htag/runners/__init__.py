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
from .pyscript import PyScript

try:
    # mono instance
    from .browserstarlettehttp import BrowserStarletteHTTP
    from .browserstarlettews import BrowserStarletteWS

    # multi instance
    from .webhttp import WebHTTP

except ImportError:
    print("**WARNING** Runners 'BrowserStarletteHTTP','BrowserStarletteWS' & 'WebHTTP' not availables, you should install 'starlette' & 'uvicorn' for theses htag runners")

try:
    # mono instance (just one pywebview ;-)
    from .pywebview import PyWebWiew
except ImportError:
    print("**WARNING** Runner 'PyWebWiew' not available, you should install 'pywebview' for this htag runner")

try:
    # mono instance (only ! htag limitation)
    from .guyapp import GuyApp
except ImportError:
    print("**WARNING** Runner 'GuyApp' not available, you should install 'guy' for this htag runner")

try:
    # mono instance (just one chrome app instance)
    from .chromeapp import ChromeApp
except ImportError:
    print("**WARNING** Runner 'ChromeApp' not available, you should install 'starlette' & 'uvicorn' for this htag runner")

