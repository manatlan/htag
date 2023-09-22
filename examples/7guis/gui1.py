import sys
from htag import Tag # the only thing you'll need ;-)


class Gui1(Tag.body):

    def init(self):
        self.value=0

    def render(self):
        self.clear()
        self <= Tag.Span( self.value )
        self <= Tag.Button( "+", _onclick=self.bind.inc() )

    def inc(self):
        self.value+=1

App=Gui1
if __name__=="__main__":
    # and execute it in a pywebview instance
    from htag.runners import *
    PyWebWiew( Gui1 ).run()

    # here is another runner, in a simple browser (thru ajax calls)
    # BrowserHTTP( Page ).run()
