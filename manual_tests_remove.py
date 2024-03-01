#!./venv/bin/python3
# -*- coding: utf-8 -*-
from htag import Tag # the only thing you'll need ;-)



class Button(Tag.button):
    def init(self,txt):
        # we set some html attributs
        self["class"]="my"                      # set @class to "my"
        self["onclick"]=self.onclick            # bind a js event on @onclick
        self<= txt

    def onclick(self):
        print("REMOVE",self.innerHTML)
        self.remove()


class Page(Tag.body): # define a <body>, but the renderer will force it to <body> in all cases
    """ This is the main Tag, it will be rendered as <body> by the htag/renderer """
    statics = b"function error(m) {document.body.innerHTML += m}",".fun {background: red}"
    def init(self):

        self <= Button("A")
        self <= Button("A2")
        self <= Button("A3")
        self <= Button("A4")
        self <= Button("A5")
        self <= Tag.button("error", _onclick=lambda o: fdsgdfgfdsgfds())

        self <= Tag.button("print",_onclick=self.print,_class="ki")

    def print(self,o):
        print("Should appear", o["class"])
        o["class"].toggle("fun")

class Page2(Tag.body): # define a <body>, but the renderer will force it to <body> in all cases
    def init(self):
        self+="Hello"
        self+=Tag.a("remover",_href="/p")


App=Page

# and execute it in a pywebview instance
from htag.runners import *
# PyWebWiew( Page ).run()

# here is another runner, in a simple browser (thru ajax calls)
# ChromeApp( Page ).run()
# BrowserHTTP( Page ).run()
app=DevApp( Page )
app.add_route("/p", lambda request: app.handle( request, Page ) )
app.add_route("/b", lambda request: app.handle( request, Page2 ) )
if __name__ == "__main__":
    # BrowserTornadoHTTP( Page ).run()
    app.run()
