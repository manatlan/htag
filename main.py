
# -*- coding: utf-8 -*-
# the simplest htag'app, in the best env to start development (hot reload/refresh)

from htag import Tag

class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self += "Hello World"
        self += Tag.button("Say hi", _onclick=self.sayhi)

    def sayhi(self,o):
        self+="hi!"

#=================================================================================
from htag.runners import Runner

if __name__=="__main__":
    Runner(App).run()
