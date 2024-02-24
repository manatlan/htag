#!./venv/bin/python3
from htag import Tag # the only thing you'll need ;-)



class Page(Tag.body):
    def init(self):
        self <= Tag.button("nimp", _onclick=self.print)
        self <= Tag.input( _onkeyup=self.print)

    def print(self,o):
        print(o.event)

App=Page

# and execute it in a pywebview instance
from htag.runners import *
# PyWebWiew( Page ).run()

# here is another runner, in a simple browser (thru ajax calls)
# ChromeApp( Page ).run()
# BrowserHTTP( Page ).run()
app=DevApp( Page )
if __name__ == "__main__":
    # BrowserTornadoHTTP( Page ).run()

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.INFO)
    logging.getLogger("htag.tag").setLevel( logging.INFO )


    app.run()
