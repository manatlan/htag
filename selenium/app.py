import sys
sys.path.insert(0,"..")
#######################################################
from htag import Tag
from htag.runners import *

class App(Tag.body):
    def init(self):
        def say_hello(o):
            self <= Tag.li("hello")
        self<= Tag.button("click",_onclick = say_hello)
        self<= Tag.button("exit",_onclick = lambda o: self.exit())

BrowserHTTP(App).run( openBrowser=False )
