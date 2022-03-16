import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from htag import Tag

# "https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css"
# css=Tag.style("""/*! bulma.io v0.8.2 | MIT License | github.com/jgthms/bulma *""")

css=Tag.link( _href="https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css",_rel="stylesheet")

class CptWithStars(Tag):
    statics=css

    def __init__(self,value=0,**a):
        Tag.__init__(self,**a)

        self.nb=value
        self.build()

    def build(self): # special method
        self.clear()
        self.add( Tag.button( "-",_onclick=self.bind.onclick(-1) ))
        self.add( self.nb )
        self.add( Tag.button( "+",_onclick=self.bind.onclick(1) ))
        for i in range(self.nb):
            self.add("*")

    def onclick(self,v):
        self.nb+=v
        self.build()


class Cpt(Tag):
    statics=css

    def __init__(self,value=0,**a):
        Tag.__init__(self,**a)
        self.nb=value

        self.ocpt = Tag.span( self.nb )

        self <= Tag.button( "-",_onclick=self.bind.onclick(-1) )
        self <= self.ocpt
        self <= Tag.button( "+",_onclick=self.bind.onclick(1) )

    def onclick(self,v):
        self.nb+=v
        self.ocpt.clear()
        self.ocpt.add(self.nb)

import time,asyncio

class Page(Tag):
    statics=css

    def __init__(self,**a):
        Tag.__init__(self,**a)
        self.c1=CptWithStars(0)
        self.c2=Cpt(0)

        self.add( self.c1 )
        self.add( self.c2 )
        self.add( Tag.button("alert",_onclick="alert(document.querySelector('input').value)",_class="button") )

        self.t=Tag.input(_value="",_onkeyup=self.bind.press(b"this.value"))
        self.add( self.t )

        s=Tag.div()
        s<= Tag.button("BUG JS pre",_onclick=self.bind.bugjs(txt=b"gfdsfsgfds()"),_class="button")
        s<= Tag.button("BUG JS post",_onclick=self.bind.bugjs(),_class="button")
        s<= Tag.button("BUG PY (normal)",_onclick=self.bind.bugpy(),_class="button")
        s<= Tag.button("BUG PY (gen)",_onclick=self.bind.bugpysg(),_class="button")
        s<= Tag.button("BUG PY (async gen)",_onclick=self.bind.bugpyag(),_class="button")
        self <= s

        self.add( Tag.button("Sync Yield",_onclick=self.bind.testSYield(),_class="button") )
        self.add( Tag.button("ASync Yield",_onclick=self.bind.testAYield(),_class="button") )

        self.js="console.log(42)"


    def press(self,v):
        self.t["value"]=v
        print(v)
        return

    def testSYield(self):
        for i in list("ABCDEF"):
            self(f"console.log('{i}')")
            time.sleep(0.5)
            print(i)
            self.add( i )
            yield

    async def testAYield(self):
        for i in list("ABCDEF"):
            self(f"console.log('{i}')")
            await asyncio.sleep(0.5)
            print(i)
            self.add( i )
            yield

    def bugpy(self):
        a=12/0
    async def bugpyag(self):
        yield
        a=12/0
        yield
    def bugpysg(self):
        yield
        a=12/0
        yield
    def bugjs(self,txt=""):
        self("fgdsgfd()")


if __name__=="__main__":
    # exemple for instanciating the logging before ...
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)


    app=Page()

    from htag.runners import *
    # r=GuyApp( app )
    # r=PyWebWiew( app )
    # r=BrowserStarletteHTTP( app )
    # r=BrowserStarletteWS( app )
    r=BrowserHTTP( app )
    # r=WebHTTP( lambda: Page() )
    r.run()

