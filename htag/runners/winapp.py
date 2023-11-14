# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

from .. import Tag
from ..render import HRenderer
from . import commons
from .chromeapp import _ChromeApp

import traceback,sys
import os,json,asyncio,html
import tornado.ioloop
import tornado.web
import tornado.websocket


import logging
logger = logging.getLogger(__name__)

class WinApp:

    """ This a "Chrome App Runner" : it runs the front in a "Chrome App mode" by re-using
    the current chrome installation, in a headless mode.

    It's the same as ChromeApp (which it reuses) ... BUT :
    - the backend use HTTP/WS with tornado (not uvicorn !!!!)
    - as it doesn't use uvicon, it's the perfect solution on windows (for .pyw files)
    """

    def __init__(self,tagClass:Tag,file:"str|None"=None):
        self._hr_session=commons.SessionFile(file) if file else None
        assert issubclass(tagClass,Tag)
        self.tagClass = tagClass
        self.hrenderer = None

        self._routes=[]

        try: # https://bugs.python.org/issue37373 FIX: tornado/py3.8 on windows
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except:
            pass

    def run(self, host="127.0.0.1", port=8000 , size=(800,600)):   # localhost, by default !!

        def instanciate(url:str):
            init = commons.url2ak(url)
            if self.hrenderer and self.hrenderer.init == init:
                return self.hrenderer

            # ws.onerror and ws.onclose shouldn't be visible, because server side stops all when socket close !
            js = """

async function interact( o ) {
    ws.send( JSON.stringify(o) );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = start;
ws.onmessage = function(e) {
    action( e.data );
};
ws.onerror = function(e) {
    console.error("WS ERROR");
};
ws.onclose = function(e) {
    window.close();
};
"""
            return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init, fullerror=False, session=self._hr_session)

        class MainHandler(tornado.web.RequestHandler):
            async def get(this):
                self.hrenderer = instanciate( str(this.request.uri) )
                this.write( str(self.hrenderer) )

        async def _sendactions(ws, actions:dict) -> bool:
            try:
                await ws.write_message( json.dumps(actions) )
                return True
            except Exception as e:
                logger.error("Can't send to socket, error: %s",e)
                return False

        class SocketHandler(tornado.websocket.WebSocketHandler):
            def open(this):
                # declare hr.sendactions (async method)
                self.hrenderer.sendactions = lambda actions: _sendactions(this,actions)

            async def on_message(this, data):
                data=json.loads(data)
                actions = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
                await _sendactions( this, actions )

            def on_close(this):
                self.chromeapp.exit()
                os._exit(0)

        try:
            self.chromeapp = _ChromeApp(f"http://{host}:{port}",size=size)
        except:
            import webbrowser
            webbrowser.open_new_tab(f"http://{host}:{port}")
            class FakeChromeApp:
                def wait(self,thread):
                    pass
                def exit(self):
                    pass
            self.chromeapp = FakeChromeApp()
        handlers=[(r"/", MainHandler),(r"/ws", SocketHandler)]
        for path,handler in self._routes:
            handlers.append( ( path,handler ) )
        app = tornado.web.Application(handlers)
        app.listen(port)
        tornado.ioloop.IOLoop.current().start()

    def add_handler(self, path:str, handler:tornado.web.RequestHandler):
        self._routes.append( (path,handler) )
