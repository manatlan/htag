from thag import Tag


class Button(Tag):

    # this Tag will be rendered as a <button>, so we set its attribut "tag" <- "button"
    tag="button"

    # this allow you to include statics in headers
    # (it will be included only once !!!)
    statics = [Tag.style("button.my {background:yellow; border:1px solid black; border-radius:4px}")]

    def __init__(self,txt, callback):
        super().__init__()

        # we set some html attributs
        self["class"]="my"                      # set @class to "my"
        self["onclick"]=self.bind.onclick()     # bind a js event on @onclick

        self <= txt                             # put a text into the button

        self.callback=callback                  # save the py callback for later use

    def onclick(self):
        # this is the event called by the @onclick
        # it will call the py callback
        self.callback()

class Star(Tag):
    # it doesn't define its "tag" attribut, so it will be a <div> (the default)

    def __init__(self,value=0):
        super().__init__()
        self.nb=value

    def inc(self,v):
        self.nb+=v

    def __str__(self):
        # here, the representation is built lately
        # (during the __str__ rendering)

        # we clear all the contents of the tag
        self.clear()

        # we add our buttons, binded to its py method
        self <= Button( "-", lambda: self.inc(-1) )
        self <= Button( "+", lambda: self.inc(1) )

        # we draw the stars
        self <= "⭐"*self.nb
        return super().__str__()


class Page(Tag):
    # it doesn't define its "tag" attribut
    # but as long as it's the main tag ...
    # it will be rendered as <body>

    def __init__(self):
        super().__init__()

        # here is a list of movies ;-)
        self.movies=[
            ("BatMan", Star(5)),
            ("Thor", Star(9)),
            ("Superman", Star(7)),
        ]

    def __str__(self):
        # here, the representation is built lately
        # (during the __str__ rendering)

        # we clear the content
        self.clear()

        # we put a title
        self <= Tag.h1("Best movies ;-)")

        # and add our stuff, sorted by nb of stars
        for name,star in sorted( self.movies, key=lambda x: -x[1].nb ):
            self <= Tag.div( [name,star] )

        return super().__str__()

obj=Page()


# here, the demo is executed in a pywebview instance
from thag.runners import *
PyWebWiew( obj ).run()

# BrowserHTTP( obj ).run()
