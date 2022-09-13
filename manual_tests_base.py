import sys
from tkinter import TRUE
from htag import Tag # the only thing you'll need ;-)



class Page(Tag.body):
    def init(self):
        self <= Tag.button("nimp", _onclick=self.print)
        self <= Tag.input( _onkeyup=self.print)

    def print(self,o):
        print(o.event)

# and execute it in a pywebview instance
from htag.runners import *
# PyWebWiew( Page ).run()

# here is another runner, in a simple browser (thru ajax calls)
# ChromeApp( Page ).run()
# BrowserHTTP( Page ).run()
app=BrowserHTTP( Page )
if __name__ == "__main__":
    # BrowserTornadoHTTP( Page ).run()
    app.run()
