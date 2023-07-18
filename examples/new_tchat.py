
# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

import asyncio,sys,time

from htag import Tag

class TagConvShared(Tag.div):
    ll=[]           # \_ class properties (shared with instances)
    instances={}    # /

    def init(self,identity):
        self.identity = identity
        TagConvShared.instances[self.identity]=self

        self.redraw()

    def redraw(self):
        self.clear()
        for id,txt in reversed(TagConvShared.ll):
            self+=Tag.li(f"{id} : {txt}")

    async def add_entry(self,txt):
        TagConvShared.ll.append( (self.identity,txt) )

        for id,obj in TagConvShared.instances.items():
            obj.redraw()
            await obj.update()


class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self.oconv=TagConvShared( identity=str(id(self)) )

        of=Tag.form()
        of["onsubmit"] = self.bind.post(b"this.txt.value") + "return false"
        of+=Tag.span(f"User {self.oconv.identity} ")
        of+=Tag.input(_name="txt")
        of+=Tag.button("post")

        self+=of
        self+=Tag.hr()
        self+=self.oconv

    async def post(self,txt):
        await self.oconv.add_entry( txt )


#================================================================================= with update capacity
from htag.runners import WebWS as Runner                    #<= the only one which will work (coz multi instance/session)
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import ChromeApp as Runner
# from htag.runners import WinApp as Runner
# from htag.runners import DevApp as Runner
#=================================================================================

app=Runner(App)
if __name__=="__main__":
    app.run()
