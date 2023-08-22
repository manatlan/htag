
# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

import asyncio,sys,time

from htag import Tag

class TagConvShared(Tag.div):
    """
    This is very special component. It has 2 goals:
    - manage an unique representation of the conversation (tchat exchanges)
    - redraw the representation on each client/instance, in live (with tag.update())

    This component can only work in some runners :
    - the runner should handle many client (think 'web' .. another web-session should open another htag instance)
    - the instances should be shared in the same process (only webws do this)

    The ONLY runner which can run this correctly is **WebWS**.
    (WebHTTP doesn't support tag.update() (http is not bi-directionnal))
    (others runners, with websockets, are "mono instance" (manage only one user/web-session))
    """
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
        if "me" not in self.state:
            self.state["me"] = str(time.time())

        self.oconv=TagConvShared( identity=self.state["me"] )

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


#================================================================================= runner with update capacity
from htag.runners import WebWS as Runner                    #<= the only one which will work (coz multi instance/session)
#=================================================================================

app=Runner(App)
if __name__=="__main__":
    app.run()
