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
    from .devapp import DevApp                                      # special dev

    # multi instance
    from .webhttp import WebHTTP

except ImportError:
    print("**WARNING** Runners 'BrowserStarletteHTTP','BrowserStarletteWS' & 'WebHTTP' (and DevApp) not availables, you should install 'starlette' & 'uvicorn' for theses htag runners")

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


try:
    # mono instance (just one android app instance)
    from .androidapp import AndroidApp
    from .browsertornadohttp import BrowserTornadoHTTP
except ImportError:
    print("**WARNING** Runner 'AndroidApp' & 'BrowserTornadoHTTP' not available, you should install 'tornado' for this htag runner")

