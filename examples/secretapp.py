# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

"""
Here is an example of an Htag App, runned in an own-made runner (see below)
which encrypt/decrypt exchanges between client/front and server/back,
for privacy needs !

the concept : encrypt/decrypt methods should exist in js and py sides
(doing the same kind of encryption/decyption ;-) )
(here, for the example: just a simple base64 encode/decode)

But you could encrypt/decrypt communications with AES/CBC and a master pass
in both sides. To avoid MITM/proxy to capture exchanges ;-)
The concepts are the same.
"""


# #############################################################################
# the Htag app
# #############################################################################

from htag import Tag

class App(Tag.body):

    def init(self):
        self <= Tag.button("test",_onclick=self.print)

    def print(self,o):
        self += "hello"



# #############################################################################
# here is a specific runner (inspired from BrowserStarletteHTTP), which
# encrypt/decrypt exchanges between client/front/ui and server/back/python
# #############################################################################

from htag import Tag
from htag.render import HRenderer
from htag.runners import common

import os

from starlette.applications import Starlette
from starlette.responses import HTMLResponse,PlainTextResponse
from starlette.routing import Route


import base64,json
def encrypt(str:str):
    return base64.b64encode(str.encode()).decode()
def decrypt(s:bytes):
    return base64.b64decode(s).decode()


class SecretApp(Starlette):
    """ Same as BrowserStarletteHTTP

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        self.hrenderer = None
        self.tagClass = tagClass

        Starlette.__init__(self,debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/', self.POST, methods=["POST"]),
        ])

    def instanciate(self,url:str):
        init = common.url2ak(url)
        if self.hrenderer and self.hrenderer.init == init:
            return self.hrenderer

        js = """

function encrypt(str) {return btoa(str)}
function decrypt(str) {return atob(str)}

async function interact( o ) {
    action( decrypt( await (await window.fetch("/",{method:"POST", body: encrypt(JSON.stringify(o))})).text() ) );
}

window.addEventListener('DOMContentLoaded', start );
"""

        return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init)

    async def GET(self,request) -> HTMLResponse:
        self.hrenderer = self.instanciate( str(request.url) )
        return HTMLResponse( str(self.hrenderer) )

    async def POST(self,request) -> PlainTextResponse:
        data = json.loads( decrypt(await request.body()) )
        dico = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
        return PlainTextResponse( encrypt( json.dumps(dico) ) )

    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        import uvicorn,webbrowser
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self, host=host, port=port)



# #############################################################################
# the runner part
# #############################################################################
app=SecretApp( App )
if __name__ == "__main__":
    app.run()
