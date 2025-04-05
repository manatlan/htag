#!./venv/bin/python3
from htag import Tag # the only thing you'll need ;-)

def nimp(obj):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


class MyTag(Tag.span):
    def __init__(self,titre,callback):
        self.titre = titre
        super().__init__( titre + Tag.Button("x",_class="delete",_onclick=callback), _class="tag",_style="margin:4px" )


class Page(Tag.body):

    def init(self):

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
        self <= Tag.button( "Stream In", _onclick=lambda o: self.stream() ) # stream in current button !
        self <= Tag.button( "Stream Out", _onclick=self.bind( self.stream ))    # stream in parent obj
        self <= Tag.button( "Stream Out", _onclick=self.bind.stream() )

        self <= "<hr>"

        # NEW MECHANISM
        self <= Tag.button( "externe (look in console)", _onclick=nimp )
        self <= Tag.button( "lambda", _onclick=lambda o: ffw(o,"lambda") )
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        #/\ try something new (multiple callbacks as a list)
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        self <= Tag.button( "**NEW**", _onclick=[ff,self.mm,lambda o: ffw(o,"KIKI")] )
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
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

    def stream(self):
        yield "a"
        yield "b"
        yield ["c","d"]
        yield MyTag("kiki", nimp)

App=Page
from htag.runners import DevApp as Runner
app=Runner( Page )
if __name__ == "__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    logging.getLogger("htag.tag").setLevel( logging.INFO )
    app.run()