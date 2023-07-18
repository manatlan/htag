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

    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)
        self.tagClass = tagClass
        self.hrenderer = None

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
    console.error("WS CLOSED");
};
"""
            return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init, fullerror=False)

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
                print("!!! exit on socket.close !!!")
                self.chromeapp.exit()
                os._exit(0)

        self.chromeapp = _ChromeApp(f"http://{host}:{port}",size=size)
        app = tornado.web.Application([(r"/", MainHandler),(r"/ws", SocketHandler)])
        app.listen(port)
        tornado.ioloop.IOLoop.current().start()
