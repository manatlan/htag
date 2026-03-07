
# -*- coding: utf-8 -*-

from htag import Tag

class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self <= "Hello World"
        self <= Tag.button("Say hi", _onclick=self.sayhi)

    def sayhi(self,ev):
        self <= "hi!"


#=================================================================================
from htag.runners import Runner

if __name__ == "__main__":
    Runner(App).run()
