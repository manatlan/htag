# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag,expose

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# an htag Tag, to use hashchange events
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
class View(Tag.div):
    def __init__(self,tag=None,**a):  # use complex constructor to do complex things ;-)
        super().__init__(tag,**a)    
        self.default = tag
        self._refs={}
        self.js = """
if(!window._hashchange_listener) {
    window.addEventListener('hashchange',() => {self._hashchange(document.location.hash);});
    window._hashchange_listener=true;
}
"""
    @expose
    def _hashchange(self,hash):
        self.clear( self._refs.get(hash, self.default) )

    def go(self,tag,anchor=None):
        """ Set object 'tag' in the View, and navigate to it """
        anchor=anchor or str(id(tag))
        self._refs[f'#{anchor}'] = tag
        self.call( f"document.location=`#{anchor}`")
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

class Page1(Tag.span):
    def init(self):
        self+="Page 1"

class Page2(Tag.div):
    def init(self):
        self+="Page 2"

class App(Tag.body):
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

app=Runner( App )
if __name__=="__main__":
    app.run()
