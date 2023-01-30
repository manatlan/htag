import sys,os
sys.path.insert(0,os.path.join( os.path.dirname(__file__),".."))
#######################################################
from htag import Tag

class App(Tag.body):
    def init(self):
        def say_hello(o):
            self <= Tag.li("hello")
        self<= Tag.button("click",_onclick = say_hello)
        self<= Tag.button("exit",_onclick = lambda o: self.exit())

#######################################################
import htag.runners
runner = getattr( htag.runners, sys.argv[1])
app=runner(App)
if runner in [htag.runners.AndroidApp,htag.runners.WebHTTP,]:
    app.run()
else:
    app.run( openBrowser=False )
