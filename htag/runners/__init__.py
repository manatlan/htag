# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

class _RunnerNotFunctionnal:
    def __init__(self,*tagClass:type):
        raise ERROR


# mono instance
from .browserhttp import BrowserHTTP

# multi instances                                                   !!! CAN UPDATE !!!
from .pyscript import PyScript


try:
    # mono instance
    from .browserstarlettehttp import BrowserStarletteHTTP
except Exception as err:
    ERROR=err
    class BrowserStarletteHTTP(_RunnerNotFunctionnal): pass

try:
    # mono instance # !                                             !! CAN UPDATE !!!
    from .browserstarlettews import BrowserStarletteWS
except Exception as err:
    ERROR=err
    class BrowserStarletteWS(_RunnerNotFunctionnal): pass

try:
    # mono instance #                                               !!! CAN UPDATE !!!
    from .webws import WebWS
except Exception as err:
    ERROR=err
    class WebWS(_RunnerNotFunctionnal): pass

try:
    # mono instance #                                               !!! CAN UPDATE !!!
    from .devapp import DevApp                                      # special dev
except Exception as err:
    ERROR=err
    class DevApp(_RunnerNotFunctionnal): pass

try:
    # multi instance
    from .webhttp import WebHTTP
except Exception as err:
    ERROR=err
    class WebHTTP(_RunnerNotFunctionnal): pass

try:
    # mono instance (just one pywebview ;-)
    from .pywebview import PyWebView
except Exception as err:
    ERROR=err
    class PyWebWiew(_RunnerNotFunctionnal): pass

try:
    # mono instance (just one chrome app instance)                  !!! CAN UPDATE !!!
    from .chromeapp import ChromeApp
except Exception as err:
    ERROR=err
    class ChromeApp(_RunnerNotFunctionnal): pass


try:
    # mono instance (just one chrome app instance)                  !!! CAN UPDATE !!!
    from .winapp import WinApp
except Exception as err:
    ERROR=err
    class WinApp(_RunnerNotFunctionnal): pass

try:
    # mono instance (just one android app instance)
    from .androidapp import AndroidApp
except Exception as err:
    ERROR=err
    class AndroidApp(_RunnerNotFunctionnal): pass

try:
    # mono instance
    from .browsertornadohttp import BrowserTornadoHTTP
except Exception as err:
    ERROR=err
    class BrowserTornadoHTTP(_RunnerNotFunctionnal): pass

