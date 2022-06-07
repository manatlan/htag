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


import os,json
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route,WebSocketRoute
from starlette.endpoints import WebSocketEndpoint

class BrowserStarletteWS(Starlette):
    """ Simple ASync Web Server (with starlette) with WebSocket interactions with HTag.
        Open the rendering in a browser tab.

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)
        js = """
async function interact( o ) {
    ws.send( JSON.stringify(o) );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = start;
ws.onmessage = function(e) {
    action( JSON.parse(e.data) );
};
"""

        self.renderer=HRenderer(tagClass, js, lambda: os._exit(0))

        class WsInteract(WebSocketEndpoint):
            encoding = "json"

            async def on_receive(this, websocket, data):
                actions = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
                await websocket.send_text( json.dumps(actions) )

        Starlette.__init__(self,debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            WebSocketRoute("/ws", WsInteract),
        ])


    async def GET(self,request):
        return HTMLResponse( str(self.renderer) )

    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        import uvicorn,webbrowser
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self, host=host, port=port)