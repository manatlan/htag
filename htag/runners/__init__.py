# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

from .runner import Runner,HTTPResponse
class _RunnerNotFunctionnal:
    def __init__(self,*tagClass:type):
        raise ERROR

# multi instances                                                   !!! CAN UPDATE !!!
from .pyscript import PyScript

def deprecated(self):
    print(f"**DEPRECATED**, replace this '{self.__class__.__name__}' by the new runner, before 1.0.0 ;-) !!!")

# mono instance
# from .browserhttp import BrowserHTTP

class BrowserHTTP(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file,http_only=True)
    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = 1 if openBrowser else 0
        Runner.run(self)


# try:
#     # mono instance
#     from .browserstarlettehttp import BrowserStarletteHTTP
# except Exception as err:
#     ERROR=err
#     class BrowserStarletteHTTP(_RunnerNotFunctionnal): pass


class BrowserStarletteHTTP(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file,http_only=True)
    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = 1 if openBrowser else 0
        Runner.run(self)


# try:
#     # mono instance # !                                             !! CAN UPDATE !!!
#     from .browserstarlettews import BrowserStarletteWS
# except Exception as err:
#     ERROR=err
#     class BrowserStarletteWS(_RunnerNotFunctionnal): pass

class BrowserStarletteWS(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file)
    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = 1 if openBrowser else 0
        Runner.run(self)

# try:
#     # mono instance #                                               !!! CAN UPDATE !!!
#     from .devapp import DevApp                                      # special dev
# except Exception as err:
#     ERROR=err
#     class DevApp(_RunnerNotFunctionnal): pass

class DevApp(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file,debug=True,reload=True,use_first_free_port=True)
    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = 1 if openBrowser else 0
        Runner.run(self)



try:
    # mono instance (just one pywebview ;-)
    from .pywebview import PyWebView
except Exception as err:
    ERROR=err
    class PyWebWiew(_RunnerNotFunctionnal): pass

# try:
#     # mono instance (just one chrome app instance)                  !!! CAN UPDATE !!!
#     from .chromeapp import ChromeApp
# except Exception as err:
#     ERROR=err
#     class ChromeApp(_RunnerNotFunctionnal): pass

class ChromeApp(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file,use_first_free_port=True)
    def run(self, host="127.0.0.1", port=8000 , size=(800,600)):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = size
        Runner.run(self)

# try:
#     # mono instance (just one chrome app instance)                  !!! CAN UPDATE !!!
#     from .winapp import WinApp
# except Exception as err:
#     ERROR=err
#     class WinApp(_RunnerNotFunctionnal): pass

class WinApp(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file,use_first_free_port=True)
    def run(self, host="127.0.0.1", port=8000 , size=(800,600)):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = size
        Runner.run(self)


# try:
#     # mono instance (just one android app instance)
#     from .androidapp import AndroidApp
# except Exception as err:
#     ERROR=err
#     class AndroidApp(_RunnerNotFunctionnal): pass

##----> AndroidApp will never be replaced (coz runner works in android/buildozer/p4a with 'webview' bootstrap)

class AndroidApp(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None,port=12458):
        deprecated(self)
        print("NOW, it has non-sense ... the htagpak recipe will change soon to show you the new way, to do it")
        Runner.__init__(self,tagClass,file,interface=0,port=port,use_first_free_port=False)   # port is defined in buildozer.specs
    def run(self):   # localhost, by default !!
        Runner.run(self)

# try:
#     # mono instance
#     from .browsertornadohttp import BrowserTornadoHTTP
# except Exception as err:
#     ERROR=err
#     class BrowserTornadoHTTP(_RunnerNotFunctionnal): pass

class BrowserTornadoHTTP(Runner):
    def __init__(self,tagClass:type,file:"str|None"=None):
        deprecated(self)
        Runner.__init__(self,tagClass,file,http_only=True)
    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        self.host=host
        self.port=port
        self.interface = 1 if openBrowser else 0
        Runner.run(self)
