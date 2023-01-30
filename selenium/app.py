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
from htag.runners import BrowserHTTP
app=BrowserHTTP(App)
if __name__=="__main__":
    app.run( openBrowser=False )
