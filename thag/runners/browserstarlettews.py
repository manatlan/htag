# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/thag
# #############################################################################

from .. import Tag
from ..render import HRenderer


import webbrowser,os,json
try:
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import HTMLResponse
except ImportError:
    import sys
    print("You should install 'starlette' & 'uvicorn' for this thag runner")
    sys.exit(-1)


class BrowserStarletteWS:
    """ Simple ASync Web Server (with starlette) with WebSocket interactions with Thag.
        Open the rendering in a browser tab.
    """
    def __init__(self,tag:Tag):
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

        self.renderer=HRenderer(tag, js, lambda: os._exit(0))


    def run(self):
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

        webbrowser.open_new_tab("http://127.0.0.1:8000")
        uvicorn.run(app)
