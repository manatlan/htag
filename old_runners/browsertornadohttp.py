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

import os,json,sys,asyncio

import tornado.ioloop
import tornado.web


class BrowserTornadoHTTP:
    """ Simple ASync Web Server (with TORNADO) with HTTP interactions with htag.
        Open the rendering in a browser tab.
    """
    def __init__(self,tagClass:Tag,file:"str|None"=None):
        self._hr_session=commons.SessionFile(file) if file else None
        assert issubclass(tagClass,Tag)

        self.hrenderer=None
        self.tagClass=tagClass

        self._routes=[]

        try: # https://bugs.python.org/issue37373 FIX: tornado/py3.8 on windows
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except:
            pass

    def instanciate(self,url:str):
        init = commons.url2ak(url)
        if self.hrenderer and self.hrenderer.init == init:
            return self.hrenderer

        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).text() )
}

window.addEventListener('DOMContentLoaded', start );
"""
        return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init,session=self._hr_session)


    def run(self, host="127.0.0.1", port=8000 , openBrowser=True):   # localhost, by default !!

        class MainHandler(tornado.web.RequestHandler):
            async def get(this):
                self.hrenderer = self.instanciate( str(this.request.uri) )
                this.write( str(self.hrenderer) )
            async def post(this):
                data = json.loads( this.request.body.decode() )
                dico = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
                this.write(json.dumps(dico))

        if openBrowser:
            import webbrowser
            webbrowser.open_new_tab(f"http://{host}:{port}")

        handlers=[(r"/", MainHandler),]
        for path,handler in self._routes:
            handlers.append( ( path,handler ) )
        app = tornado.web.Application( handlers )
        app.listen(port)
        tornado.ioloop.IOLoop.current().start()

    def add_handler(self, path:str, handler:tornado.web.RequestHandler):
        self._routes.append( (path,handler) )
