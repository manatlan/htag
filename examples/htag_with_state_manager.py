# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

"""
For bigger project ... it's a good practice to start
with an unique "source of truth" (all data in one place).

Here is a example

Principes:
- You make a private dict in your htag component -> THE store
  (all data will be read/write from here)
- In your component, you only have read access on this store.
- and ONLY yours (inter-)actions can mutate this store

See pinia/vuex for vuejs, redux for react, or ngrx for angular, etc ...
"""

from htag import Tag
from dataclasses import dataclass

# the DB simulation part
#.......................................................................
@dataclass
class Product:
    name: str
    price: int

PRODUCTS={
    "ref1":Product("Peach",10),
    "ref4":Product("Apple",2),
    "ref5":Product("Pear",3),
    "ref7":Product("Banana",3),
}

# a class to provide only readacess to your store (dict)
#.......................................................................
class Store:
    def __init__(self, store:dict ):
        self.__store = store
    def __getitem__(self,k):
        return self.__store.get(k)


# the components :
#.......................................................................
class PageList(Tag.div):
    def init(self):
        self <= Tag.h1("Products")
        for ref,p in PRODUCTS.items():
            d=Tag.div(_style="border:1px dotted black;display:inline-block;width:100px;height:100px")
            d<=Tag.h3(p.name)
            d<=Tag.button("View", value=ref, _onclick = lambda o: self.root.action('SELECT',selected=o.value) )
            d<=Tag.button("Add", value=ref,_onclick = lambda o: self.root.action('ADD',selected=o.value) )
            self <= d

class PageProduct(Tag.div):
    def init(self,ref):
        p = PRODUCTS[ref]

        b=Tag.button("back", _onclick = lambda o: self.root.action('LISTE') )
        self <= Tag.h1(b+f"Products > {p.name}")
        self <= Tag.h3(f"Price: {p.price}€")
        self <= Tag.button("Add", _onclick = lambda o: self.root.action('ADD',selected=ref) )

class Basket(Tag.div):

    def render(self): # dynamic rendering (so it can react on store changes)
        liste = self.root.store["baskets"]

        self.clear()
        if liste:
            somme=0
            for ref in liste:
                p = PRODUCTS[ref]
                self <= Tag.li( f"{p.name}: {p.price}€" )
                somme+=p.price
            self <= Tag.b(f"Total: {somme}€")
            self <= Tag.button("clear", _onclick = lambda o: self.root.action('CLEAR') )
        else:
            self <= "vide"

# and your main tag (which will be runned in a runner)
#.......................................................................

class App(Tag.body):
    def init(self):
        # the private store
        self.__store = {"baskets": []}

        # the public store (read only)
        self.store = Store( self.__store )

        # prepare layout
        self.main = Tag() # placeholder !

        # draw layout
        self <= self.main + Tag.div(Basket(),_style="position:fixed;top:0px;right:0px;background:yellow")

        # 1st action
        self.action("LISTE")

    def action(self, action, **params):
        """ here are the mutations for your actions
            The best practice : the store is mutated only in this place !
        """
        if action == "LISTE":
            self.main.clear(PageList() )
        elif action == "SELECT":
            self.main.clear(PageProduct( params["selected"] ) )
        elif action == "ADD":
            self.__store["baskets"].append( params["selected"] )
        elif action == "CLEAR":
            self.__store["baskets"] = []

        print("NEW STORE:",self.__store)

# the runner part
#.......................................................................
from htag.runners import DevApp as Runner
# from htag.runners import BrowserHTTP as Runner
# from htag.runners import ChromeApp as Runner


app=Runner(App)
if __name__=="__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    logging.getLogger("htag.tag").setLevel( logging.ERROR )
    logging.getLogger("htag.render").setLevel( logging.ERROR )
    logging.getLogger("uvicorn.error").setLevel( logging.ERROR )
    logging.getLogger("asyncio").setLevel( logging.ERROR )
    app.run()
