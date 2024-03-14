
# -*- coding: utf-8 -*-

import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import asyncio,sys,time


from htag import Tag


class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self.place = Tag.div(js="console.log('I update myself')")

        asyncio.ensure_future( self.loop_timer() )

        self += "Hello World" + self.place
        self+= Tag.button("yo",_onclick=self.doit)

    async def doit(self,o):
        self+="x"

    async def loop_timer(self):
        while 1:
            await asyncio.sleep(0.5)
            self.place.clear(time.time() )
            if not await self.place.update(): # update component using current websocket
                # break if can't (<- good practice to kill this asyncio/loop)
                break



#================================================================================= with update capacity
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import ChromeApp as Runner
# from htag.runners import WinApp as Runner
from htag.runners import DevApp as Runner
#=================================================================================

#~ from htagweb import WebServer as Runner
# from htag.runners import BrowserHTTP as Runner

app=Runner(App)

if __name__=="__main__":
    app.run()
