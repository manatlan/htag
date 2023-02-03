import sys
from htag import Tag # the only thing you'll need ;-)



class Page(Tag.body):
    def init(self):
        self.call.redraw()

    def clir(self,o):
        self.session.clear()
        self.redraw()

    def redraw(self):
        self.clear()
        self <= Tag.button("add", _onclick=self.sett)
        self <= Tag.button("clir", _onclick=self.clir)
        self+=self.session.get("toto","?")

    def sett(self,o):
        self.session["toto"]=self.session.get("toto",0) + 1
        self.redraw()


# and execute it in a pywebview instance
from htag.runners import *

app=WebHTTP( Page )
if __name__ == "__main__":
    # BrowserTornadoHTTP( Page ).run()

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    logging.getLogger("htag.tag").setLevel( logging.INFO )


    app.run()
