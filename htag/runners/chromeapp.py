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

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse
from starlette.routing import Route

#="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="="
#
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

    BTW : it uses Starlette/http as backend server
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).json() )
}

window.addEventListener('DOMContentLoaded', start );
"""

        host,port= "127.0.0.1", 8707
        self._chromeapp = _ChromeApp(f"http://{host}:{port}",size=(800,600))
        self.renderer=HRenderer(tagClass, js, self._chromeapp.exit )

        asgi=Starlette(debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/', self.POST, methods=["POST"]),
        ])

        self._server = threading.Thread(name='ChromeAppServer', target=uvicorn.run,args=(asgi,),kwargs=dict(host=host, port=port))

    async def GET(self,request) -> HTMLResponse:
        return HTMLResponse( str(self.renderer) )

    async def POST(self,request) -> JSONResponse:
        data = await request.json()
        dico = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"])
        return JSONResponse(dico)

    def run(self):
        self._server.start()
        self._chromeapp.wait()
        os._exit(0) # to force quit the thread/uvicorn server
