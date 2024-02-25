
# -*- coding: utf-8 -*-
# the simplest htag'app, in the best env to start development (hot reload/refresh)

from htag import Tag

class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self += "xxx World!!!"

#=================================================================================
from htag.runners import BrowserHTTP as Runner
# from htag.runners import BrowserHTTP as Runner
# from htag.runners import ChromeApp as Runner

app=Runner(App)
if __name__=="__main__":
    app.run()
