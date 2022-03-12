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

""" REAL WEB http,
- .exit() has no effect ;-)
- can handle multiple client (see SESID below)
- each client -> an instance is created (at post)
- session are destroyed after 5m of inactivity
"""

import os
import time
import asyncio

TIMEOUT = 5*60 # in seconds

try:
    import uvicorn
    from starlette.applications import Starlette
    from starlette.responses import HTMLResponse,JSONResponse
    from starlette.routing import Route
except ImportError:
    import sys
    print("You should install 'starlette' & 'uvicorn' for this thag runner")
    sys.exit(-1)


class WebHTTP:
    """ Simple ASync Web Server (with starlette) with HTTP interactions with Thag.
        can handle multiple instances !!!
    """
    def __init__(self,callback_tag_creator):
        self.sessions={}
        self.callback_tag_creator = callback_tag_creator

    def _createRenderer(self):
        js = """
async function interact( o ) {
    action( await (await window.fetch("/"+SESID,{method:"POST", body:JSON.stringify(o)})).json() )
}

//======================================================= create a unique SESSION ID
var SESID = window.sessionStorage.getItem('SESID');
if(!SESID) {
    SESID = Math.random().toString(36).substring(2);
    window.sessionStorage.setItem('SESID',SESID);
}
console.log("SESSION ID:",SESID)
//=======================================================

window.addEventListener('DOMContentLoaded', start );
"""
        tag = self.callback_tag_creator()
        return HRenderer(tag, js ) # NO EXIT !!

    def _getRendererSession(self,ses_id):

        if ses_id in self.sessions: # reuse
            ses_renderer = self.sessions[ses_id]["renderer"]
        else: # create a new one
            ses_renderer = self._createRenderer()
            self.sessions[ses_id] = dict( lastaccess=None, renderer=ses_renderer )

        self.sessions[ses_id]["lastaccess"] = time.time()
        return self.sessions[ses_id]["renderer"]

    async def _purgeSessions(self):

        async def purge():
            while True:
                now=time.time()
                for ses_id,ses_info in list(self.sessions.items()):
                    if now - ses_info["lastaccess"] > TIMEOUT:
                        del self.sessions[ses_id]

                await asyncio.sleep(60) # every 60s

        asyncio.ensure_future( purge() )


    async def GET(self,request) -> HTMLResponse:
        # create a "empty shelf" (the renderer is destroyed after use)
        r=self._createRenderer()
        return HTMLResponse( str(r) )

    async def POST(self,request) -> JSONResponse:
        data=await request.json()

        # get renderer from session id
        ses_renderer = self._getRendererSession(request.path_params['sesid'])

        actions = await ses_renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
        return JSONResponse(actions)

    def run(self, host="0.0.0.0", port=8000):   # wide, by default !!
        app = Starlette(debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/{sesid}', self.POST, methods=["POST"]),
        ], on_startup=[self._purgeSessions])
        uvicorn.run(app, host=host, port=port)
