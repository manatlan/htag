#!./venv/bin/python3
# -*- coding: utf-8 -*-

from htag import Tag
import asyncio,time

class App(Tag.body):

    def init(self,param="nada"):
        self["style"]="background:#EEE;"
        self <= Tag.h3("param = "+param)
        self <= Tag.a("test '?' ?",_href="?",_style="display:block")
        self <= Tag.a("test '?param=A1'",_href="?param=A1",_style="display:block")
        self <= Tag.a("test '?param=A2'",_href="?param=A2",_style="display:block")
        self <= Tag.button("error", _onclick=lambda o: fdsgdfgfdsgfds())
        self <= Tag.button("add content", _onclick=self.add_content)    # just to control interact
        self <= Tag.button("EXIT app", _onclick=lambda o: self.exit())    # just to test QUIT/EXIT app
        self <= Tag.hr()

        self <= Tag.h3("Only if it handles tha '/other' route (DevApp/htagweb) :")
        self <= Tag.a("test '/other'"      ,_href="/other",_style="display:block")
        self <= Tag.a("test '/other?pablo'",_href="/other?pablo",_style="display:block")
        self <= Tag.hr()

        self <= Tag.iframe(_src="/item/42")

        # self.place=Tag.div("this should be updated... no?")
        # self <= self.place
        # asyncio.ensure_future( self.loop_timer() )

    async def loop_timer(self):
        while 1:
            await asyncio.sleep(0.5)
            self.place.clear(time.time() )
            if not await self.place.update(): # update component (without interaction)
                # break if can't (<- good practice to kill this asyncio/loop)
                print("asyncio loop stopped")
                break


    def add_content(self,o):
        self <= "X "


#=================================================================================
#---------------------------------------------------------------------------------
# from htag.runners import DevApp as Runner     # with .serve() and no QUIT

# from htag.runners import BrowserHTTP as Runner
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import BrowserStarletteHTTP as Runner
# from htag.runners import BrowserTornadoHTTP as Runner
# from htag.runners import ChromeApp as Runner
# from htag.runners import AndroidApp as Runner
# from htag.runners import PyWebView as Runner  # just the "add content" will work (no query params / no other route)

from htag.runners import Runner,HTTPResponse
app=Runner(App,reload=False,debug=True,interface=(400,400),use_first_free_port=True)

class AnotherApp(Tag.body):

    def init(self, name="vide"):
        self["style"]="background:#FFE;"
        self <= "Hello "+name
        self <= Tag.button("add content", _onclick=self.add_content)

    def add_content(self,o):
        self <= "X "

#note : no path_params/query_params in route path !
app.add_route( "/other", lambda request: app.handle(request, AnotherApp ) )


async def handlerItem( request ):
    idx=request.path_params.get("idx")
    txt=request.query_params.get("txt")
    return HTTPResponse(200,"Numero %d (txt=%s)" % (idx,txt))

app.add_route( "/item/{idx:int}", handlerItem )


if __name__=="__main__":
    app.run()
