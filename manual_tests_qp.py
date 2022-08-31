# -*- coding: utf-8 -*-

from htag import Tag

class App(Tag.body):

    def init(self,param="nada"):
        self["style"]="background:#EEE;"
        self <= Tag.h3("param = "+param)
        self <= Tag.a("test '/' ?",_href="/",_style="display:block")
        self <= Tag.a("test '/?param=yo'",_href="/?param=yo",_style="display:block")
        self <= Tag.button("add content", _onclick=self.add_content)    # just to control interact
        self <= Tag.button("quit app", _onclick=lambda o: self.exit())    # just to control interact
        self <= Tag.hr()

        self <= Tag.h3("Only if it handles tha '/other' route (WebHTTP/DevApp) :")
        self <= Tag.a("test '/other'"      ,_href="/other",_style="display:block")
        self <= Tag.a("test '/other?pablo'",_href="/other?pablo",_style="display:block")
        self <= Tag.hr()

    def add_content(self,o):
        self <= "X "


class AnotherApp(Tag.body):

    def init(self, name="vide"):
        self["style"]="background:#FFE;"
        self <= "Hello "+name
        self <= Tag.button("yo", _onclick=self.test)

    def test(self,o):
        self <= "X "

#=================================================================================
#---------------------------------------------------------------------------------
from htag.runners import DevApp as Runner     # with .serve() and no QUIT
# from htag.runners import WebHTTP as Runner    # with .serve() and no QUIT

# from htag.runners import BrowserHTTP as Runner
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import BrowserStarletteHTTP as Runner
# from htag.runners import BrowserTornadoHTTP as Runner
# from htag.runners import ChromeApp as Runner
# from htag.runners import AndroidApp as Runner
# from htag.runners import PyWebView as Runner  # just the "add content" will work (no query params / no other route)


app=Runner(App)

if hasattr(app,"serve"): # only DevApp & WebHTTP

    def another(request):
        return app.serve(request, AnotherApp )

    app.add_route("/other", another )


if __name__=="__main__":
    app.run()
