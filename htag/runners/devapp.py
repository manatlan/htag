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
            * js error() method auto implemented (popup with skip/refresh)

        Simple ASync Web Server (with starlette) with WebSocket interactions with HTag.
        Open the rendering in a browser tab.

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        # add a Static Template, for displaying beautiful full error on UI ;-)
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #TODO: perhaps something integrated in hrenderer
        styles={"color":"yellow","text-decoration":"none"}
        t=Tag.H.div( _style="z-index:10000000000;position:fixed;top:10px;left:10px;background:#F00;padding:8px;border:1px solid yellow" )
        t <= Tag.H.a("X",_href="#",_onclick="this.parentNode.remove()",_style=styles,_title="Forget error (skip)")
        t <= " "
        t <= Tag.H.a("REFRESH",_href="#",_onclick="window.location.reload()",_style=styles,_title="Restart the UI part by refreshing it")
        t <= Tag.H.pre(_style="overflow:auto")
        template = Tag.H.template(t,_id="DevAppError")
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\


        js = """

window.error=function(txt) {
    var clone = document.importNode(document.querySelector("#DevAppError").content, true);
    clone.querySelector("pre").innerHTML = txt
    document.body.appendChild(clone)
}

async function interact( o ) {
    let packet = JSON.stringify(o)
    console.info("[htag interact]",packet.length,o)
    ws.send( packet );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = function() {console.info("[htag start]");start()};
ws.onclose = function() {document.body.innerHTML="Refreshing";window.location.reload()}

ws.onmessage = function(e) {
    let data = JSON.parse(e.data);
    console.info("[htag action]",e.data.length,data)
    action( data );
};
"""
        self.renderer=HRenderer(tagClass, js, lambda: os._exit(0), fullerror=True, statics=[template,])

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

        os.environ["PYTHONUNBUFFERED"]="FALSE"

        if openBrowser:
            webbrowser.open_new_tab(url)
        uvicorn.run(fileapp,host=host,port=port,reload=True,debug=True)
