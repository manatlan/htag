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
from . import commons

import os,json,sys,asyncio
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route,WebSocketRoute
from starlette.endpoints import WebSocketEndpoint

import socket

import logging
logger = logging.getLogger(__name__)

def isFree(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    return not (s.connect_ex((ip,port)) == 0)

async def _sendactions(ws, actions:dict) -> bool:
    try:
        await ws.send_text( json.dumps(actions) )
        return True
    except Exception as e:
        logger.error("Can't send to socket, error: %s",e)
        return False

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

        self.hrenderers={}
        self.tagClass=tagClass

        self._ws=None

        class WsInteract(WebSocketEndpoint):
            encoding = "json"

            #=========================================================
            async def on_connect(this, websocket):

                # accept cnx
                await websocket.accept()

                # declare websocket
                self._ws=websocket
            #=========================================================

            async def on_receive(this, websocket, data):
                className = data["class"]
                actions = await self.hrenderers[className].interact(data["id"],data["method"],data["args"],data["kargs"],data["event"])
                await _sendactions( websocket, actions )

        Starlette.__init__(self,debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            WebSocketRoute("/ws", WsInteract),
        ])


    def instanciate(self, tagClass, init):
        """ intanciate or reuse """
        className = tagClass.__name__

        if className in self.hrenderers and self.hrenderers[className].init == init:
            # the current version has already be initialized, we return the saved instance
            return self.hrenderers[className]

        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        # add a Static Template, for displaying beautiful full error on UI ;-)
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\ #TODO: perhaps something integrated in hrenderer
        styles={"color":"yellow","text-decoration":"none"}
        t=Tag.div( _style="z-index:10000000000;position:fixed;top:10px;left:10px;background:#F00;padding:8px;border:1px solid yellow" )
        t <= Tag.a("X",_href="#",_onclick="this.parentNode.remove()",_style=styles,_title="Forget error (skip)")
        t <= " "
        t <= Tag.a("REFRESH",_href="#",_onclick="window.location.reload()",_style=styles,_title="Restart the UI part by refreshing it")
        t <= Tag.pre(_style="overflow:auto")
        template = Tag.template(t,_id="DevAppError")
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

        js = """

window.error=function(txt) {
    var clone = document.importNode(document.querySelector("#DevAppError").content, true);
    clone.querySelector("pre").innerHTML = txt
    document.body.appendChild(clone)
}

async function interact( o ) {
    o["class"] = "%s";
    let packet = JSON.stringify(o)
    console.info("[htag interact]",packet.length,o)
    ws.send( packet );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = function() {console.info("[htag start]");start()};
ws.onclose = function() {document.body.innerHTML="Refreshing";window.location.reload()}

ws.onmessage = function(e) {
    try {
        console.info("[htag action]",e.data.length,JSON.parse(e.data));
    }
    catch(e) {
        console.info("[htag action] ERROR:",e.data.length,e.data)
    }
    action( e.data );
};
""" % className
        self.hrenderers[className]=HRenderer(tagClass, js, self.killme, fullerror=True, statics=[template,], init=init)
        self.hrenderers[className].sendactions = lambda actions: _sendactions(self._ws,actions)

        return self.hrenderers[className]


    async def GET(self,request):
        return self.serve(request, self.tagClass )

    def serve(self,request, klass, init=None) -> HTMLResponse:
        """ Serve for the `request`, an instance of the class 'klass'
        initialized with `init` (tuple (*args,**kargs))
        if init is None : takes them from request.url ;-)

        return an htmlresponse (htag init page to start all)
        """
        if init is None:
            # no init params
            # so we take thoses from the url
            init = commons.url2ak( str(request.url) )
        else:
            assert type(init)==tuple
            assert type(init[0])==tuple
            assert type(init[1])==dict

        hr = self.instanciate( klass, init )

        return HTMLResponse( str(hr) )


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

        uvicorn.run(fileapp,host=host,port=port,reload=True)

        # config = uvicorn.Config(self,host=host,port=port,reload=True,debug=True)
        # server = uvicorn.Server(config=config)
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(server.run())
        # server.run()

    def killme(self):
        #TODO: exit() should work on devapp
        os._exit(0) # but not, coz uvicorn restart the dead process in reloader mode

