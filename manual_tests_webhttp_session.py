import sys
from htag import Tag # the only thing you'll need ;-)



class Page(Tag.body):
    def init(self):
        self.call.redraw()
        self.nb=0

    def clir(self,o):
        self.state["toto"]=0
        self.redraw()

    def redraw(self):
        self.clear()
        self <= Tag.button("add", _onclick=self.sett)
        self <= Tag.button("clir", _onclick=self.clir)
        self+=self.state.get("toto","?")
        self <= Tag.hr() + Tag.button("add", _onclick=self.addd) + Tag.span(self.nb)

    def sett(self,o):
        self.state["toto"]=self.state.get("toto",0) + 1
        self.redraw()

    def addd(self,o):
        self.nb+=1
        self.redraw()

App=Page
# and execute it in a pywebview instance
from htag.runners import *

app=WebWS( Page )
if __name__ == "__main__":
    # BrowserTornadoHTTP( Page ).run()

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    logging.getLogger("htag.tag").setLevel( logging.INFO )


    app.run()
