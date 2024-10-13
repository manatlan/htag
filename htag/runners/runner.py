# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2024 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################
from .. import Tag
from ..render import HRenderer
from . import commons

from .server import start_server,HTTPResponse

from .chromeappmode import ChromeApp

"""
the new runner features :
    - PURE python (no external dependancies)
    - ultra fast start (compared to uvicorn/starlette)
    - hot reload (init param: reload)
    - debug mode (init param: debug)
    - persistent session (init param: file)
    - auto open browser (default) (run param: openBrowser=1|True)
    - "chrome app mode", with fallback to default browser if not possible (run param: openBrowser=2 & size=(width, height))
    - can serve multiple tag (add_route method on its serve method)
    - can serve http request (add_route method ... with request with method, path, query_params & path_params) (no cookie yet)
    - can act as HTTP+WS (default) or HTTP only
    - [HTTP-WS only] tag.update !
    - [HTTP-WS only] in "chrome app mode", can quit when window is closed
    - in "chrome app mode", can quit when self.exit() is called
    - [HTTP-WS only] in browser, can quit when tab is closed 
    - [HTTP-WS only] unlike good old chromeapp/winapp : works with multiple tags (in the past: only one, which maintain cnx with socket). No it exits when no more active socket 
    - better code & better maintability, with logger (in one place!)
    - can use first free port (and launch in any cases), if port is already used

    in fact, it exposes all features from all different runners in ONE and UNIQUE place ... to be able to simulate each current runner ;-)
"""
import sys
import asyncio
import socket
import webbrowser,os,json
import urllib.parse
import logging
import traceback
import importlib,inspect,socket

logger = logging.getLogger(__name__)

def reload( tagClass ):
    try:
        mod=inspect.getmodule(tagClass)
        if mod:
            importlib.reload( mod )
            logger.debug("Reloaded %s", tagClass)
            return getattr(mod, tagClass.__name__)
        else:
            logger.debug("Can't reload %s (%s)", tagClass,"module not found")
            return tagClass
    except ModuleNotFoundError as e:
        # when tagclass is in the __main__ (the runner)
        logger.debug("Can't reload %s (%s)", tagClass,e)
        return tagClass

def isFree(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    return not (s.connect_ex((ip,port)) == 0)


def runChromeApp(host:str,port:int,size:tuple):
    """run a 'chrome in app mode', or a browser tab if it can't"""
    try:
        return ChromeApp(f"http://{host}:{port}",size=size)
    except:
        import webbrowser
        webbrowser.open_new_tab(f"http://{host}:{port}")
        class FakeChromeApp:
            def wait(self,thread):
                pass
            def exit(self):
                pass
        return FakeChromeApp()



class MyServer:
    jsinteract="alert('to override')"

    def __init__(self,host,port,session,reload:bool,routes:list,dev:bool,exit_callback):
        self.host=host
        self.port=port
        self.session=session
        self.reload = reload
        self.dev=dev
        self.exit_callback = exit_callback
        self.connected=0

        self._routes={}
        for path,handler in routes:
            self._routes[path]=dict(
                handler=handler,        # handler(request) -> HTTPResponse (ex: "lambda request: self.serve( request, tagClass)")
                hr=None,                # the hrenderer instance (managed by the runner, see .serve())
            )


    def doGet(self,realpath:str, klass, init:tuple) -> HTTPResponse:
        hr = self._routes[realpath]["hr"]
        if self.reload or hr is None or hr.init!=init:
            info="create"
            hr = self.hrcreate(klass, self.jsinteract % realpath, init)
            self._routes[realpath]["hr"]=hr
        else:
            info="reuse"
            
        logger.info("SERVE (%s) path:'%s' init:%s for class:%s -> %s",info,realpath,init,klass,repr(hr.tag))

        return HTTPResponse(200,str(hr))

    #############################################################################
    def server( self, handlerGET, handlerPOST, handlerWs ):

        async def routing(request) -> HTTPResponse:
            up=urllib.parse.urlparse(request.path)
            path = up.path # without query
            query_params = {k:v[0] for k,v in urllib.parse.parse_qs(up.query, keep_blank_values=True).items()}

            router = self._routes.get(path)
            if router:
                # direct route (aka an htag handler)
                if request.method=="GET":
                    try:
                        return await handlerGET(request,router["handler"])
                    except Exception as e:
                        print("====================================================",flush=True)
                        print("SERVER ERROR:",traceback.format_exc(),flush=True)
                        print("====================================================",flush=True)
                        return HTTPResponse(500, str(e) )                        
                elif request.method=="POST" and handlerPOST and router.get("hr"):
                    try:
                        return await handlerPOST(request,router["hr"])
                    except Exception as e:
                        print("====================================================",flush=True)
                        print("SERVER ERROR:",traceback.format_exc(),flush=True)
                        print("====================================================",flush=True)
                        return HTTPResponse(500, str(e) )  
                else:                      
                    return HTTPResponse(400, "bad request" )  
            else:
                for rpath,data in self._routes.items():
                    path_params=commons.match( rpath, path)
                    if path_params:
                        # enhance request object (TODO: cookies ?)
                        request.path_params=path_params
                        request.query_params=query_params
                        router = data["handler"]
                        try:
                            return await router(request)
                        except Exception as e:
                            print("====================================================",flush=True)
                            print("SERVER ERROR:",traceback.format_exc(),flush=True)
                            print("====================================================",flush=True)
                            return HTTPResponse(500, str(e) )                        
                        

            return HTTPResponse(404,"no route")

        return start_server(routing, handlerWs, self.host, self.port)

    #############################################################################
    def hrcreate(self,tagClass,js:str,init:tuple) -> HRenderer:
        if self.reload: tagClass = reload( tagClass )

        if self.dev:
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

            js_error=Tag.script("""
window.error=function(txt) {
    var clone = document.importNode(document.querySelector("#DevAppError").content, true);
    clone.querySelector("pre").innerHTML = txt
    document.body.appendChild(clone)
}""")

            fullerror=True
            statics=[template,js_error]
        else:
            fullerror=False
            statics=[]

        return HRenderer( tagClass , js, 
                         exit_callback = self.exit_callback,
                         fullerror=fullerror,
                         statics=statics,
                         init=init,
                         session=self.session)
    
    async def hrinteract(self, hr:HRenderer, jzon:str) -> str:
        data=json.loads(jzon)
        actions = await hr.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
        return json.dumps(actions)

class ServerWS(MyServer):
    
    jsinteract = """
async function interact( o ) {
    ws.send( JSON.stringify(o) );
}
var ws = new WebSocket("//"+document.location.host+"%s");
ws.onopen = start;
ws.onmessage = function(e) {
    action( e.data );
};
"""    
    
    def run(self):
        self.CPT=0
        async def handlerWs(ws):
            try:
                try:
                    path=urllib.parse.urlparse(ws.request.path).path
                    hr = self._routes[path]["hr"]
                except: # sometimes handlerWs is called with http path or None ?!? TODO: wtf ?
                    return

                self.connected+=1

                async def updateactions(actions:dict):
                    await ws.send( json.dumps(actions) ) 
                    return True

                hr.sendactions = updateactions

                while True:
                    frame = await ws.recv()
                    if frame is None:
                        break
                    
                    logger.debug("handlerWS: find hr for path '%s' -> %s",ws.request.path, repr(hr.tag))
                    
                    jzon = await self.hrinteract(hr, frame)
                    await ws.send( jzon )

                self.connected-=1

            except:
                print("====================================================",flush=True)
                print("WS ERROR:",traceback.format_exc(),flush=True)
                print("====================================================",flush=True)
                await ws.send( json.dumps({}) )
        
        async def handlerGET(request,handler) -> HTTPResponse:
            return handler(request)  # lambda request: self.serve( request, tagClass)

        return self.server(handlerGET, None, handlerWs)



class ServerHTTP(MyServer):
    jsinteract = """
async function interact( o ) {
    action( await (await window.fetch("%s",{method:"POST", body:JSON.stringify(o)})).text() )
}

window.addEventListener('DOMContentLoaded', start );
"""
    
    def run(self):
        async def handlerWs(ws):
            # not the biggest idea ... but it's like
            # there was no ws server ;-(
            #TODO: can do better ? me ?
            pass
        
        async def handlerGET(request,handler) -> HTTPResponse:
            self.connected=1 #never false
            return handler(request)  # lambda request: self.serve( request, tagClass)

        async def handlerPOST(request,hr) -> HTTPResponse:
            jzon = await self.hrinteract(hr, request.body.decode() )
            return HTTPResponse(200,jzon,"application/json")

        return self.server(handlerGET, handlerPOST, handlerWs)



class Runner:

    def __init__(self,
                tagClass:"type|None"=None,
                file:"str|None"=None, 
                host:str="127.0.0.1",
                port:int=8000,
                interface=1,    # 1|True -> browser (quit on exit), (width,height) -> chromeapp (fallback to browser) (quit on exit), 0|False|None -> serve forever
                reload:bool=False, 
                debug:bool=False,
                http_only:bool=False,
                use_first_free_port:bool=False,
        ):
        self.session=commons.SessionFile(file) if file else None
        self.host=host
        self.port=port
        self.debug=debug
        self.reload=reload
        self.http_only=http_only
        self.interface=interface
        self.use_first_free_port=use_first_free_port
        self._routes=[]
        
        if tagClass:
            assert issubclass(tagClass,Tag)            
            self.add_route( "/", lambda request: self.serve( request, tagClass) )

    def add_route(self,path:str,handler) -> None:
        self._routes.append( (path, handler) )
        

    def run(self): 
        if self.use_first_free_port:
            while not isFree(self.host,self.port):
                self.port+=1

        if self.http_only:
            self.server = ServerHTTP(self.host,self.port,self.session, routes=self._routes, reload=self.reload, dev=self.debug, exit_callback=self.stop)
        else:
            self.server = ServerWS(self.host,self.port,self.session, routes=self._routes, reload=self.reload, dev=self.debug, exit_callback=self.stop)

        loop = asyncio.get_event_loop()
        server = loop.run_until_complete( self.server.run() )

        self.chromeapp=None
        if self.interface:
            if self.interface in [1,True]:
                webbrowser.open_new_tab(f"http://{self.host}:{self.port}")
            elif isinstance(self.interface,tuple) and len(self.interface)==2:
                self.chromeapp = runChromeApp(self.host,self.port,self.interface)
            else:
                raise Exception("Not a good 'interface' !")

            if not self.http_only:
                logger.debug("watchdog will control socket connexions")
                # kill server if 'interface' is closed (only ServerWS!)
                async def watchdog():

                    logger.debug("watchdog waiting 1st connexion")
                    while self.server.connected==0:
                        await asyncio.sleep(0.1)

                    logger.debug("watchdog connected, handle the life")
                    nb=4
                    while 1:
                        await asyncio.sleep(0.5)
                        #print(self.server.connected,flush=True)
                        if self.server.connected==0:
                            nb-=1
                            if nb<1: self.stop()
                        else:
                            nb=3
                loop.create_task( watchdog() )
            else:
                print("***WARNING*** the server won't autoquit when interface is closed",flush=True)

        try:
            loop.run_forever()
        except KeyboardInterrupt as e:
            #TODO: gracefull exit with CTRl-C !!!!
            server.close()
            loop.run_until_complete(server.wait_closed())
        finally:
            loop.close()
            self.stop()

    def stop(self):
        if self.chromeapp:
            self.chromeapp.exit()
            self.chromeapp=None
        os._exit(0)


    # DEPRECATED
    def serve(self, request, tagClass:type) -> HTTPResponse:
        return self.handle( request, tagClass )
    
    def handle(self, request, tagClass:type) -> HTTPResponse:
        assert issubclass(tagClass,Tag)            

        init = commons.url2ak( str(request.path) )      # a init tuple
        path = urllib.parse.urlparse(request.path).path # path without query_params !
    
        return self.server.doGet( path, tagClass, init )

    def __str__(self):
        return f"<Runner {self.host}:{self.port} debug:{self.debug} reload:{self.reload} routes:{self._routes}>"
        
