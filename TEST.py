#!/usr/bin/python
# -*- coding: utf-8 -*-
from htag import H,Tag


class Inputer(Tag.input):
    
    def __init__(self,onchange):
        Tag.__init__(self)
        self["value"] = ""
        self.onchange = onchange
        
        self["onchange"] = self.bind._onchange(b"this.value")

    @Tag.NoRender
    def _onchange(self,v):
        self["value"] = v
        self.onchange(v)

class App(Tag.body):
    def __init__(self):
        Tag.__init__(self)
        
        self.box = Tag.div()
        self <= "Good:"
        self <= Inputer( onchange = lambda v: self.box.set(v) )
        self <= self.box
        self <= "<hr>"
        
        #Not GOOOD ! box2 is a TagBase, it's not updatable lonely
        # --> NOW IT'S GOOD !
        self.box2 = Tag.div()   
        self <= "Bad:"
        self <= Inputer( onchange = lambda v: self.box2.set(v) )
        self <= self.box2
        self <= "<hr>"

        #Not GOOOD ! box3 is in A TagBase, it's not updatable lonely
        # --> NOW IT'S GOOD !
        self.box3 = Tag.div()   
        self <= Tag.div( [
            "bad",
            Inputer( onchange = lambda v: self.box3.set(v) ),
            self.box3,
        ])
        self <= "<hr>"


#~ t=H.div("hello")
#~ print(repr(t),t)
#~ quit()

if __name__=="__main__":
    app = App()
    
    import logging
    logging.basicConfig(level = logging.DEBUG)

    logger = logging.getLogger("htag.tag")
    logger.setLevel(logging.ERROR)

    from htag.runners import *
    # r=GuyApp( app )
    r=PyWebWiew( app )
    # r=BrowserStarletteHTTP( app )
    # r=BrowserStarletteWS( app )
    #~ r=BrowserHTTP( app )
    # r=WebHTTP( lambda: Page() )
    r.run()
