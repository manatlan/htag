import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag

"""
This example show you how to make a "Calc App"
(with physical buttons + keyboard events)

There is no work for rendering the layout ;-)

Can't be simpler !

"""

class Calc(Tag.div):
    statics=[Tag.H.style("""
.mycalc *,button {font-size:2em;font-family: monospace}
""")]

    def __init__(self):
        self.txt=""
        self.aff = Tag.Div("&nbsp;",_style="border:1px solid black")
        super().__init__(self.aff,_class="mycalc")
        self <= Tag.button("C", _onclick=self.bind( self.clean) )
        self <= [Tag.button(i,  _onclick=self.bind( self.press, i) ) for i in "0123456789+-x/."]
        self <= Tag.button("=", _onclick=self.bind( self.compute ) )

    #-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/ with real keyboard
        self["onkeyup"] = self.bind( self.presskey, b"event.key" )

    def presskey(self,key):
        if key in "0123456789+-*/.":
            self.press(key)
        elif key=="Enter":
            self.compute()
        elif key in ["Delete","Backspace"]:
            self.clean()
    #-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/

    def press(self,val):
        self.txt += val
        self.aff.set( self.txt )

    def compute(self):
        try:
            self.txt = str(eval(self.txt.replace("x","*")))
            self.aff.set( self.txt )
        except:
            self.txt = ""
            self.aff.set( "Error" )

    def clean(self):
        self.txt=""
        self.aff.set("&nbsp;")

if __name__=="__main__":
    # import logging
    # logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.getLogger("htag.tag").setLevel( logging.INFO )

    # and execute it in a pywebview instance
    from htag.runners import *

    # here is another runner, in a simple browser (thru ajax calls)
    BrowserHTTP( Calc ).run()
    # PyWebWiew( Calc ).run()
