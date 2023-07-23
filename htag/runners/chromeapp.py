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
from . import commons

import os

import uvicorn,json
from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse
from starlette.routing import Route
from starlette.routing import Route,WebSocketRoute
from starlette.endpoints import WebSocketEndpoint

#="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="
# mainly code from the good old guy ;-)
#="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="
import sys
import shutil
import tempfile
import subprocess
import logging
import threading
import webbrowser

logger = logging.getLogger(__name__)

class FULLSCREEN: pass
CHROMECACHE=".cache"

class _ChromeApp:
    def __init__(self, url, appname="driver",size=None,lockPort=None,chromeargs=[]):

        def find_chrome_win():
            import winreg  # TODO: pip3 install winreg

            reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
            for install_type in winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE:
                try:
                    with winreg.OpenKey(install_type, reg_path, 0, winreg.KEY_READ) as reg_key:
                        return winreg.QueryValue(reg_key, None)
                except WindowsError:
                    pass

        def find_chrome_mac():
            default_dir = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists(default_dir):
                return default_dir


        if sys.platform[:3] == "win":
            exe = find_chrome_win()
        elif sys.platform == "darwin":
            exe = find_chrome_mac()
        else:
            for i in ["chromium-browser", "chromium", "google-chrome", "chrome"]:
                try:
                    exe = webbrowser.get(i).name
                    break
                except webbrowser.Error:
                    exe = None

        if not exe:
            raise Exception("no chrome browser, no app-mode !")
        else:
            args = [ #https://peter.sh/experiments/chromium-command-line-switches/
                exe,
                "--app=" + url, # need to be a real http page !
                "--app-id=%s" % (appname),
                "--app-auto-launched",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-notifications",
                "--disable-features=TranslateUI",
                #~ "--no-proxy-server",
            ] + chromeargs
            if size:
                if size == FULLSCREEN:
                    args.append("--start-fullscreen")
                else:
                    args.append( "--window-size=%s,%s" % (size[0],size[1]) )

            if lockPort: #enable reusable cache folder (coz only one instance can be runned)
                self.cacheFolderToRemove=None
                args.append("--remote-debugging-port=%s" % lockPort)
                args.append("--disk-cache-dir=%s" % CHROMECACHE)
                args.append("--user-data-dir=%s/%s" % (CHROMECACHE,appname))
            else:
                self.cacheFolderToRemove=os.path.join(tempfile.gettempdir(),appname+"_"+str(os.getpid()))
                args.append("--user-data-dir=" + self.cacheFolderToRemove)
                args.append("--aggressive-cache-discard")
                args.append("--disable-cache")
                args.append("--disable-application-cache")
                args.append("--disable-offline-load-stale-cache")
                args.append("--disk-cache-size=0")

            logger.debug("CHROME APP-MODE: %s"," ".join(args))
            # self._p = subprocess.Popen(args)
            self._p = subprocess.Popen(args,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            #~ if lockPort:
                #~ http_client = tornado.httpclient.HTTPClient()
                #~ self._ws = None
                #~ while self._ws == None:
                    #~ try:
                        #~ url = http_client.fetch("http://localhost:%s/json" % debugport).body
                        #~ self._ws = json.loads(url)[0]["webSocketDebuggerUrl"]
                    #~ except Exception as e:
                        #~ self._ws = None

    def wait(self):
        self._p.wait()

    def __del__(self): # really important !
        self._p.kill()
        if self.cacheFolderToRemove: shutil.rmtree(self.cacheFolderToRemove, ignore_errors=True)

    #~ def _com(self, payload: dict):
        #~ """ https://chromedevtools.github.io/devtools-protocol/tot/Browser/#method-close """
        #~ payload["id"] = 1
        #~ r=json.loads(wsquery(self._ws,json.dumps(payload)))["result"]
        #~ return r or True

    #~ def focus(self): # not used
        #~ return self._com(dict(method="Page.bringToFront"))

    #~ def navigate(self, url): # not used
        #~ return self._com(dict(method="Page.navigate", params={"url": url}))

    def exit(self):
        #~ self._com(dict(method="Browser.close"))
        self._p.kill()
#="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="


class ChromeApp:
    """ This a "Chrome App Runner" : it runs the front in a "Chrome App mode" by re-using
    the current chrome installation, in a headless mode.
    (it's a little bit like pywebview/cef technics, but based on the real installed chrome)

    new: you can set a host & a size (tuple (width,height)) at run (like WinApp)

    BTW : it uses Starlette/http as backend server
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        self.hrenderer = None
        self.tagClass = tagClass


    def instanciate(self,url:str):
        init = commons.url2ak(url)
        if self.hrenderer and self.hrenderer.init == init:
            return self.hrenderer

        # ws.onerror and ws.onclose shouldn't be visible, because server side stops all when socket close !
        js = """

async function interact( o ) {
    ws.send( JSON.stringify(o) );
}

var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = start;
ws.onmessage = function(e) {
    action( e.data );
};
ws.onerror = function(e) {
    console.error("WS ERROR");
};
ws.onclose = function(e) {
    console.error("WS CLOSED");
};
"""
        return HRenderer(self.tagClass, js, self._chromeapp.exit, init=init )


    async def GET(self,request) -> HTMLResponse:
        self.hrenderer = self.instanciate( str(request.url) )
        return HTMLResponse( str(self.hrenderer) )

    def run(self, host="127.0.0.1", port=8000 , size=(800,600)):   # localhost, by default !!
        self._chromeapp = _ChromeApp(f"http://{host}:{port}",size=size)

        async def _sendactions(ws, actions:dict) -> bool:
            try:
                await ws.send_text( json.dumps(actions) )
                return True
            except Exception as e:
                logger.error("Can't send to socket, error: %s",e)
                return False

        class WsInteract(WebSocketEndpoint):
            encoding = "json"

            #=========================================================
            async def on_connect(this, websocket):

                # accept cnx
                await websocket.accept()

                # declare hr.sendactions (async method)
                self.hrenderer.sendactions = lambda actions: _sendactions(websocket,actions)

            #=========================================================
            async def on_receive(this, websocket, data):
                actions = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
                await _sendactions( websocket, actions )

            async def on_disconnect(this, websocket, close_code):
                print("!!! exit on socket.close !!!")
                self._chromeapp.exit()
                os._exit(0)

        asgi=Starlette(debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            WebSocketRoute("/ws", WsInteract),
        ])

        self._server = threading.Thread(name='ChromeAppServer', target=uvicorn.run,args=(asgi,),kwargs=dict(host=host, port=port))
        self._server.start()
        self._chromeapp.wait()
        os._exit(0) # to force quit the thread/uvicorn server
