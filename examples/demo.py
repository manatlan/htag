import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from thag import Tag


class Button(Tag):
    tag="button"
    statics = [Tag.style("button.my {background:yellow; border:1px solid black; border-radius:4px}")]

    def __init__(self,txt, callback):
        super().__init__()
        self["class"]="my"
        self <= txt
        self["onclick"]=self.bind.onclick()
        self.callback=callback

    def onclick(self):
        self.callback()

class Star(Tag):

    def __init__(self,value=0):
        super().__init__()
        self.nb=value

    def inc(self,v):
        self.nb+=v

    def __str__(self):
        self.clear()
        self <= Button( "-", lambda: self.inc(-1) )
        self <= Button( "+", lambda: self.inc(1) )
        self <= "⭐"*self.nb
        return super().__str__()


class Page(Tag):

    def __init__(self):
        super().__init__()

        self.movies=[
            ("BatMan", Star(5)),
            ("Thor", Star(9)),
            ("Superman", Star(7)),
        ]

    def __str__(self):
        self.clear()
        self <= Tag.h1("Best movies ;-)")
        for name,star in sorted( self.movies, key=lambda x: -x[1].nb ):
            self <= Tag.div( [name,star] )
        return super().__str__()

obj=Page()
from thag.runners import *
# BrowserHTTP( obj ).run()
PyWebWiew( obj ).run()