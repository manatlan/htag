import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from htag import Tag
import htbulma as b

class App(Tag):

    def __init__(self,**a):
        super().__init__(**a)

        self._mbox = b.MBox(self)
        self <= Tag.button("test", _onclick=self.bind.test())

    def test(self): #TODO: make an UNITTEST for this
        oi = b.InputText("")
        oi.js = "tag.focus()"

        def giveAnswer(v):
            self<=Tag.li(v)

        self._mbox.confirm(
            b.Content( [Tag.h1("What's your name ?"),oi] ),
            ok=lambda : giveAnswer(oi.value),
        )

if __name__=="__main__":
    app = App()

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)


    from htag.runners import *
    # r=GuyApp( app )
    # r=PyWebWiew( app )
    # r=BrowserStarletteHTTP( app )
    # r=BrowserStarletteWS( app )
    r=BrowserHTTP( app )
    # r=WebHTTP( lambda: Page() )
    r.run()

