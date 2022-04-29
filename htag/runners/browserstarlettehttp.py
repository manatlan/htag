# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

from .. import Tag
from ..render import HRenderer

import webbrowser,os

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse
from starlette.routing import Route


class BrowserStarletteHTTP:
    """ Simple ASync Web Server (with starlette) with HTTP interactions with htag.
        Open the rendering in a browser tab.
    """
    def __init__(self,tag:Tag):
        assert isinstance(tag,Tag)

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
        data = await request.json()
        dico = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
        return JSONResponse(dico)


    def __call__(self):
        """ create a uvicorn factory/asgi, to make it compatible with uvicorn
            from scratch.
        """
        return Starlette(debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/', self.POST, methods=["POST"]),
        ])
        return app

    def run(self, host="127.0.0.1", port=8000, openBrowser=True, debug=True):   # localhost, by default !!
        import uvicorn
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self(), host=host, port=port)

