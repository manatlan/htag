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

import threading
import os,json
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route,WebSocketRoute
from starlette.endpoints import WebSocketEndpoint

import socket

def isFree(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    return not (s.connect_ex((ip,port)) == 0)

class DevApp(Starlette):
    """ DEV APP, Runner specialized for development process. Features :
            * autoreload on file changes
            * refresh UI/HTML/client part, after server autoreloaded
            * console.log/info in devtools, for all exchanges
            * uvicorn debug
            * js error() method auto implemented

        Simple ASync Web Server (with starlette) with WebSocket interactions with HTag.
        Open the rendering in a browser tab.

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)
        js = """

window.error=function(txt) {document.body.innerHTML = txt+" <a href='#' onclick='window.location.reload()'>Restart</a>"}

async function interact( o ) {
    console.info("[htag interact]",o)
    ws.send( JSON.stringify(o) );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = function() {console.info("[htag start]");start()};
ws.onclose = function() {window.location.reload()}

ws.onmessage = function(e) {
    let data = JSON.parse(e.data);
    console.info("[htag action]",data)
    action( data );
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
        """ example `app.run(__name__)` """
        import uvicorn,webbrowser
        import inspect,sys
        from pathlib import Path

        try:
            fi= inspect.getframeinfo(sys._getframe(1))
            stem = Path(fi.filename).stem
            instanceName = fi.code_context[0].strip().split(".")[0]
        except Exception as e:
            print("Can't run DevApp :",e)
            sys.exit(-1)

        fileapp = stem+":"+instanceName
        url = f"http://{host}:{port}"
        print("="*79)
        print(f"Start Uvicorn Reloader for '{fileapp}' ({url})")
        print("="*79)

        if openBrowser:
            webbrowser.open_new_tab(url)
        uvicorn.run(fileapp,host=host,port=port,reload=True,debug=True)

