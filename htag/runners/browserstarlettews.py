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


import os,json
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route,WebSocketRoute
from starlette.endpoints import WebSocketEndpoint

import logging
logger = logging.getLogger(__name__)


class BrowserStarletteWS(Starlette):
    """ Simple ASync Web Server (with starlette) with WebSocket interactions with HTag.
        Open the rendering in a browser tab.

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)
        self.hrenderer = None
        self.tagClass = tagClass

        async def _sendactions(ws, actions:dict) -> bool:
            try:
                await ws.send_text( json.dumps(actions) )
                return True
            except Exception as e:
                logger.error("Can't send to socket, error: %s",e)
                return False


        class WsInteract(WebSocketEndpoint):
            encoding = "json"

            #=========================================================
            async def on_connect(this, websocket):

                # accept cnx
                await websocket.accept()

                # declare hr.sendactions (async method)
                self.hrenderer.sendactions = lambda actions: _sendactions(websocket,actions)

            #=========================================================

            async def on_receive(this, websocket, data):
                actions = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
                await _sendactions( websocket, actions )

        Starlette.__init__(self,debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            WebSocketRoute("/ws", WsInteract),
        ])


    def instanciate(self,url:str):
        init = commons.url2ak(url)
        if self.hrenderer and self.hrenderer.init == init:
            return self.hrenderer

        js = """
async function interact( o ) {
    ws.send( JSON.stringify(o) );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = start;
ws.onmessage = function(e) {
    action( e.data );
};
"""
        return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init)

    async def GET(self,request):
        self.hrenderer=self.instanciate( str(request.url) )
        return HTMLResponse( str(self.hrenderer) )

    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        import uvicorn,webbrowser
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self, host=host, port=port)