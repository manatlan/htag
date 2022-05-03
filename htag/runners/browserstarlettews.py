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


import webbrowser,os,json
import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse


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

var ws = new WebSocket("ws://localhost:8000/ws");
ws.onopen = start;
ws.onmessage = function(e) {
    action( JSON.parse(e.data) );
};
"""

        self.renderer=HRenderer(tagClass, js, lambda: os._exit(0))

    def run(self, host="127.0.0.1", port=8000, openBrowser=True ):   # localhost, by default !!
        app = Starlette()

        @app.route('/')
        async def homepage(request):
            return HTMLResponse( str(self.renderer) )

        @app.websocket_route('/ws')
        async def websocket(websocket):
            await websocket.accept()
            while True:
                mesg = await websocket.receive_text()
                data = json.loads(mesg)
                actions = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
                await websocket.send_text( json.dumps(actions) )
            await websocket.close()

        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")
        uvicorn.run(app, host=host, port=port)
