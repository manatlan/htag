import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

# the simplest htag'app, in the best env to start development (hot reload/refresh)
from htag import Tag

class App(Tag.body):
    def init(self):
        self += "Hello World"

from htag.runners import DevApp as Runner           # need starlette+uvicorn !!!
#from htag.runners import BrowserHTTP as Runner
app=Runner(App)
if __name__=="__main__":
    app.run()
