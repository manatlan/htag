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

class BrowserStarletteWS:
    """ Simple ASync Web Server (with starlette) with WebSocket interactions with HTag.
        Open the rendering in a browser tab.
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

    async def GET(self,request):
        return HTMLResponse( str(self.renderer) )

    def __call__(self,*a,**k):
        """ create a uvicorn factory/asgi, to make it compatible with uvicorn
            from scratch.
        """
        class WsInteract(WebSocketEndpoint):
            encoding = "json"

            async def on_receive(this, websocket, data):
                actions = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
                await websocket.send_text( json.dumps(actions) )

        return Starlette(debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            WebSocketRoute("/ws", WsInteract),
        ])

    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        import uvicorn,webbrowser
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self(), host=host, port=port)