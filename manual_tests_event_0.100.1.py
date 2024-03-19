#!./venv/bin/python3
from htag import Tag,expose

"""
Manual Tests  (will be in selenium tests soon)
To tests all "events binding" (except async, but should be the same)
for htag >= 0.100.1
"""

#----------------------------------------------------------
# Old style (without parameter) (NO CLOSURE POSSIBLE)
#----------------------------------------------------------
class O1(Tag.span):
    """ onclick = self.bind.click() """
    def init(self):
        self <= Tag.button("test", _onclick = self.bind.click() )

    def click(self):
        assert self.event["timeStamp"]>0 # event in self
        self <= Tag.b("*")

#----------------------------------------------------------
# Old style (with parameter) (NO CLOSURE POSSIBLE)
#----------------------------------------------------------
class OP1(Tag.span):
    """ onclick = self.bind.click(42) """
    def init(self):
        self <= Tag.button("test", _onclick = self.bind.click(42,p="x") )

    def click(self,nb,p=None):
        assert self.event["timeStamp"]>0 # event in self
        assert nb==42
        assert p=="x"
        self <= Tag.b("*")


#----------------------------------------------------------
# the simplest one (cant provide own parameters)
#----------------------------------------------------------
class S1(Tag.span):
    """ onclick = self.click """
    def init(self):
        self <= Tag.button("test", _onclick = self.click )

    def click(self,o):
        assert o == self.childs[0]
        assert o.event["timeStamp"]>0
        self <= Tag.b("*")

class S1c(Tag.span):
    """ onclick = click """
    def init(self):
        def click(o):
            assert o == self.childs[0]
            assert o.event["timeStamp"]>0
            self <= Tag.b("*")
        self <= Tag.button("test", _onclick = click )


#----------------------------------------------------------
# the same ^^ (without providing own parameters)
#----------------------------------------------------------
class S2(Tag.span):
    """ onclick = b.bind(self.click) """
    def init(self):
        b=Tag.button("test")
        b["onclick"] = b.bind(self.click)
        self <= b

    def click(self, o):
        assert o == self.childs[0]
        assert o.event["timeStamp"]>0  # event in self
        self <= Tag.b("*")

class S2c(Tag.span):
    """ onclick = b.bind(click) """
    def init(self):
        
        def click(o):
            assert o == self.childs[0]
            assert o.event["timeStamp"]>0  # event in self
            self <= Tag.b("*")
        
        b=Tag.button("test")
        b["onclick"] = b.bind(click)
        self <= b


#----------------------------------------------------------
# the same ^^ (with providing own parameters)
#----------------------------------------------------------
class SP2(Tag.span): 
    """ onclick = b.bind(self.click,42) """
    def init(self):
        b=Tag.button("test")
        b["onclick"] = b.bind(self.click,42,p="x")
        self <= b

    def click(self, o, nb, p=None):
        assert o == self.childs[0]
        assert o.event["timeStamp"]>0  # event in self
        assert nb==42
        assert p=="x"
        self <= Tag.b("*")
        
class SP2c(Tag.span):
    """ onclick = b.bind(click,42) """
    def init(self):
        
        def click(o, nb, p=None):
            assert o == self.childs[0]
            assert o.event["timeStamp"]>0  # event in self
            assert nb==42
            assert p=="x"
            self <= Tag.b("*")
        
        b=Tag.button("test")
        b["onclick"] = b.bind(click,42,p="x")
        self <= b


#----------------------------------------------------------
# using self.bind (without providing own parameters)
#----------------------------------------------------------
class S3(Tag.span):
    """ onclick = self.bind(self.click) """
    def init(self):
        self <= Tag.button("test", _onclick = self.bind(self.click) )

    def click(self):
        assert self.event["timeStamp"]>0  # event in self
        self <= Tag.b("*")

class S3c(Tag.span):
    """ onclick = self.bind(click) """
    def init(self):
        def click(self):
            assert self.event["timeStamp"]>0  # event in self
            self <= Tag.b("*")
        
        self <= Tag.button("test", _onclick = self.bind(click) )


#----------------------------------------------------------
# using self.bind (with providing own parameters)
#----------------------------------------------------------
class SP3(Tag.span):
    """ onclick = self.bind(self.click,42) """
    def init(self):
        self <= Tag.button("test", _onclick = self.bind(self.click,42,p="x") )

    def click(self,nb,p=None):
        assert self.event["timeStamp"]>0  # event in self
        assert nb==42
        assert p=="x"
        self <= Tag.b("*")

class SP3c(Tag.span):
    """ onclick = self.bind(click,42) """
    def init(self):
        def click(self,nb,p=None):
            assert self.event["timeStamp"]>0  # event in self
            assert nb==42
            assert p=="x"
            self <= Tag.b("*")
        
        self <= Tag.button("test", _onclick = self.bind(click,42,p="x") )



#----------------------------------------------------------
# With "ev" : the simplest one (cant provide own parameters)
#----------------------------------------------------------
class E1(Tag.span):
    """ onclick = self.click """
    def init(self):
        self <= Tag.button("test", _onclick = self.click )

    def click(self,ev):
        assert ev.target == self.childs[0]
        assert ev.timeStamp >0
        self <= Tag.b("*")

class E1c(Tag.span):
    """ onclick = click """
    def init(self):
        def click(ev):
            assert ev.target == self.childs[0]
            assert ev.timeStamp >0
            self <= Tag.b("*")
        self <= Tag.button("test", _onclick = click )


#----------------------------------------------------------
# With "ev" :the same ^^ (without providing own parameters)
#----------------------------------------------------------
class E2(Tag.span):
    """ onclick = b.bind(self.click) """
    def init(self):
        b=Tag.button("test")
        b["onclick"] = b.bind(self.click)
        self <= b
        
    def click(self,ev):
        assert ev.target == self.childs[0]
        assert ev.timeStamp >0
        self <= Tag.b("*")


class E2c(Tag.span):
    """ onclick = b.bind(click) """
    def init(self):
        def click(ev):
            assert ev.target == self.childs[0]
            assert ev.timeStamp >0
            self <= Tag.b("*")
        
        b=Tag.button("test")
        b["onclick"] = b.bind(click)
        self <= b
        
#----------------------------------------------------------
# With "ev" : the same ^^ (with providing own parameters)
#----------------------------------------------------------
class EP2(Tag.span):
    """ onclick = b.bind(self.click,42) """
    def init(self):
        b=Tag.button("test")
        b["onclick"] = b.bind(self.click,42,p="x")
        self <= b
        
    def click(self,ev,nb,p=None):
        assert ev.target == self.childs[0]
        assert ev.timeStamp >0
        assert nb==42
        assert p=="x"
        self <= Tag.b("*")


class EP2c(Tag.span):
    """ onclick = b.bind(click,42) """
    def init(self):
        def click(ev,nb,p=None):
            assert ev.target == self.childs[0]
            assert ev.timeStamp >0
            assert nb==42
            assert p=="x"
            self <= Tag.b("*")
        
        b=Tag.button("test")
        b["onclick"] = b.bind(click,42,p="x")
        self <= b
        

#----------------------------------------------------------
# using self.bind (without providing own parameters)
#----------------------------------------------------------
class E3(Tag.span):
    """ onclick = self.bind(self.click) """
    def init(self):
        self <= Tag.button("test",_onclick=self.bind(self.click))
        
    def click(self,ev):
        assert ev.target == self
        assert ev.timeStamp >0
        self <= Tag.b("*")


class E3c(Tag.span):
    """ onclick = self.bind(click) """
    def init(self):
        def click(ev):
            assert ev.target == self
            assert ev.timeStamp >0
            self <= Tag.b("*")
        
        self <= Tag.button("test",_onclick=self.bind(click))

#----------------------------------------------------------
# using self.bind (with providing own parameters)
#----------------------------------------------------------
class EP3(Tag.span):
    """ onclick = self.bind(self.click,42) """
    def init(self):
        self <= Tag.button("test",_onclick=self.bind(self.click,42,p="x"))
        
    def click(self,ev,nb,p=None):
        assert ev.target == self
        assert ev.timeStamp >0
        assert nb==42
        assert p=="x"
        self <= Tag.b("*")


class EP3c(Tag.span):
    """ onclick = self.bind(click,42) """
    def init(self):
        def click(ev,nb,p=None):
            assert ev.target == self
            assert ev.timeStamp >0
            assert nb==42
            assert p=="x"
            self <= Tag.b("*")
        
        self <= Tag.button("test",_onclick=self.bind(click,42,p="x"))


################################################################

class Prez(Tag.div):
    def init(self,i):
        if i.__class__.__name__.startswith("E"):
            self["class"]="info ev"
        else:
            self["class"]="info"
        self+= Tag.div(i.__class__.__name__+":"+i.__doc__) + i
        
class App(Tag.body):
    statics=Tag.style("""
    .info {
        border-top: 1px dotted #AAA;
        padding: 4px;
    }
    .ev {background:#EEE}
    .info > div {
        display:inline-block;
        width:300px;
    }
    """),Tag.script("""
function testall( ) {
    for(let i of document.querySelectorAll("button")) i.click()
    setTimeout( function() {document.body.valid( document.querySelectorAll("b").length ) }, 100 )
}
    """)

    def init(self):
        self.oresult = Tag.i( Tag.a("**TEST ALL**",_href="#",_onclick="testall()"), _style="float:right" )
        self+= self.oresult
        
        self+=Tag.h4("old style:")
        for i in [O1(),OP1()]:
            self <= Prez(i)
        self+=Tag.h4("bind'style:")
        for i in [S1(),S1c(),S2(),S2c(),SP2(),SP2c(),S3(),S3c(),SP3(),SP3c()]:
            self <= Prez(i)
        self+=Tag.h4("bind'ev style:")
        for i in [E1(),E1c(),E2(),E2c(),EP2(),EP2c(),E3(),E3c(),EP3(),EP3c()]:
            self <= Prez(i)


    @expose
    def valid(self,nb):
        nbtest=len([i for i in self.childs if isinstance(i,Prez)])
        self.oresult.clear( "OK" if nbtest == nb else "KO" )



if __name__=="__main__":
    from htag.runners import Runner
    Runner(App,debug=True,reload=True).run()
