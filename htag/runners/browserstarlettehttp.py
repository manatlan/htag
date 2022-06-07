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

import os

from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse
from starlette.routing import Route


class BrowserStarletteHTTP(Starlette):
    """ Simple ASync Web Server (with starlette) with HTTP interactions with htag.
        Open the rendering in a browser tab.

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).json() )
}

window.addEventListener('DOMContentLoaded', start );
"""

        self.renderer=HRenderer(tagClass, js, lambda: os._exit(0))

        Starlette.__init__(self,debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/', self.POST, methods=["POST"]),
        ])

    async def GET(self,request) -> HTMLResponse:
        return HTMLResponse( str(self.renderer) )

    async def POST(self,request) -> JSONResponse:
        data = await request.json()
        dico = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
        return JSONResponse(dico)

    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        import uvicorn,webbrowser
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self, host=host, port=port)

