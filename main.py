
# -*- coding: utf-8 -*-

from htag import Tag

class App(Tag.body):
    statics=b"var SESID='no'"
    def init(self,param="nada"):
        self["body"]="background:#EEE;"
        self <= Tag.h3("param = "+param)
        self <= Tag.a("test SELF ?",_href="/",_style="display:block")
        self <= Tag.a("test SELF pablo",_href="/?pablo",_style="display:block")
        self <= Tag.button("yo", _onclick=self.test)    # just to control interact
        self <= Tag.button("quit", _onclick=lambda o: self.exit())    # just to control interact
        self <= Tag.hr()
        self <= Tag.h3("Only if multiples (WebServer) :")
        self <= Tag.a("test ANOTHER ?",_href="/toto",_style="display:block")
        self <= Tag.a("test ANOTHER pablo",_href="/toto?pablo",_style="display:block")


        self( self.bind.rendu( b"SESID" ) )

    def test(self,o):
        self <= "X "

    def rendu(self,x):
        self <= "SESID:"+x

class AnotherApp(Tag.body):

    def init(self, name="vide"):
        self["body"]="background:#FAA;"
        self <= "Hello "+name
        self <= Tag.button("yo", _onclick=self.test)

    def test(self,o):
        self <= "X "

#=================================================================================
#---------------------------------------------------------------------------------
# from htag.runners import DevApp as Runner     # with .serve() and no QUIT
# from htag.runners import WebHTTP as Runner    # with .serve() and no QUIT

# from htag.runners import BrowserHTTP as Runner
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import BrowserStarletteHTTP as Runner
# from htag.runners import BrowserTornadoHTTP as Runner
from htag.runners import ChromeApp as Runner


app=Runner(App)

if hasattr(app,"serve"): # only DevApp & WebHTTP
    from starlette.responses import HTMLResponse
    def another(request):
        return app.serve(request, AnotherApp )

    app.add_route("/toto", another )


if __name__=="__main__":
    app.run()
