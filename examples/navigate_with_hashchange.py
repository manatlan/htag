# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# an htag Tag, to use hashchange events
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
class View(Tag.div):
    def __init__(self,o=None,**a):  # use complex constructor to do complex things ;-)
        super().__init__(o,**a)
        self._refs={None:o}
        self.js = "window.addEventListener('hashchange',() => {%s;});" % self.bind._hashchange(b"document.location.hash")

    def _hashchange(self,hash=None):
        self.set( self._refs.get(hash or None,"???") )

    def go(self,o,anchor=None):
        """ Set object 'o' in the View, and navigate to it """
        if anchor is None: anchor=str(id(o))
        self._refs['#'+anchor] = o
        self.call( "document.location='#"+anchor+"';")
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

class Page1(Tag.span):
    def init(self):
        self+="Page 1"

class Page2(Tag.div):
    def init(self):
        self+="Page 2"

class MyApp(Tag.body):
    """ Example1: classic use (view is just a child of the body), at child level """
    def init(self):
        p0 = "welcome"  # default page
        p1 = Page1()
        p2 = Page2()

        self.v = View( p0, _style="border:1px solid red;width:100%;height:400px" )

        # layout
        self += Tag.button("p1",_onclick=lambda o: self.v.go( p1,"p1" ))
        self += Tag.button("p2",_onclick=lambda o: self.v.go( p2,"p2" ))
        self += self.v

# class MyApp(View):
#     """ Example2: The body is a 'View' (at top level) """
#     def __init__(self,**a):
#         p0 = "welcome"  # default page
#         p1 = Page1()
#         p2 = Page2()

#         # add "menus" to pages, to be able to navigate
#         sp = lambda o: self.go( o.page, o.page.__class__.__name__ )
#         menus = Tag.button("p1", page=p1, _onclick=sp) + Tag.button("p2",page=p2,_onclick=sp)
#         p1 += menus
#         p2 += menus

#         super().__init__(p0 + menus,**a)


#======================================
from htag.runners import DevApp as Runner

app=Runner( MyApp )
if __name__=="__main__":
    app.run()
