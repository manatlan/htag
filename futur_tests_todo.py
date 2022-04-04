import sys
from htag import Tag # the only thing you'll need ;-)

def nimp(obj):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


class MyTag(Tag.span):
    def __init__(self,titre,callback):
        self.titre = titre
        super().__init__( [titre,Tag.Button("x",_class="delete",_onclick=callback)], _class="tag",_style="margin:4px" )


class Page(Tag.body):

    def __init__(self):
        super().__init__()

        def ff(obj):
            self <= "ff"

        def ffw(obj,size):
            self <= "f%s" %size

        def aeff(obj):
            print(obj)
            obj <= "b"


        # EVEN NEW MECHANISM
        self <= Tag.button( "TOP", _onclick=self.bind(ffw,b"window.innerWidth") )
        self <= Tag.button( "TOP2", _onclick=self.bind(ffw,"toto") )
        self <= MyTag( "test", aeff )

        self <= "<hr>"

        # NEW MECHANISM
        self <= Tag.button( "externe", _onclick=nimp )
        self <= Tag.button( "lambda", _onclick=lambda o: ffw(o,"lambda") )
        self <= Tag.button( "ff", _onclick=ff )
        self <= Tag.button( "mm", _onclick=self.mm )
        self <= Tag.button( "ymm", _onclick=self.ymm )
        self <= Tag.button( "amm", _onclick=self.amm )
        self <= Tag.button( "aymm", _onclick=self.aymm )
        self <= "<hr>"

        # OLD MECHANISM
        self <= Tag.button( "mm", _onclick=self.bind.mm("x") )
        self <= Tag.button( "ymm", _onclick=self.bind.ymm("x") )
        self <= Tag.button( "amm", _onclick=self.bind.amm("x") )
        self <= Tag.button( "aymm", _onclick=self.bind.aymm("x") )
        self <= "<hr>"

    def mm(self,obj):
        self<="mm"

    def ymm(self,obj):
        self<="mm1"
        yield
        self<="mm2"

    async def amm(self,obj):
        self <= "amm"

    async def aymm(self,obj):
        self <= "aymm1"
        yield
        self <= "aymm2"

import logging
logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

# instanciate the main component
obj=Page()

# and execute it in a pywebview instance
from htag.runners import *
# PyWebWiew( obj ).run()

# here is another runner, in a simple browser (thru ajax calls)
BrowserHTTP( obj ).run()
