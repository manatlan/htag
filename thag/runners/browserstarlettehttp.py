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

import webbrowser,os

try:
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import HTMLResponse,JSONResponse
    from starlette.routing import Route
except ImportError:
    import sys
    print("You should install 'starlette' & 'uvicorn' for this thag runner")
    sys.exit(-1)


class BrowserStarletteHTTP:
    """ Simple ASync Web Server (with starlette) with HTTP interactions with Thag.
        Open the rendering in a browser tab.
    """
    def __init__(self,tag:Tag):
        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).json() )
}

window.addEventListener('DOMContentLoaded', start );
"""

        self.renderer=HRenderer(tag, js, lambda: os._exit(0))

    async def GET(self,request) -> HTMLResponse:
        return HTMLResponse( str(self.renderer) )

    async def POST(self,request) -> JSONResponse:
        data=await request.json()
        dico = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
        return JSONResponse(dico)

    def run(self):
        app = Starlette(debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/', self.POST, methods=["POST"]),
        ])
        webbrowser.open_new_tab("http://127.0.0.1:8000")
        uvicorn.run(app)
