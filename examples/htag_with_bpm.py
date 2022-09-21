# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

"""

BPM is a new thing ... it's a BPM (for now, only available if pyyaml is here)
Because HTAG is really convenient to be used in a BPM
Here is a example with htag.BPM .

"""

from htag import Tag,BPM


from dataclasses import dataclass

@dataclass
class Produit:
    name: str
    price: int

PRODUITS={
    "ref1":Produit("Olive",10),
    "ref4":Produit("Pomme",2),
    "ref5":Produit("Poire",3),
}


class MyBPM(BPM):
    """
    START:
        - call CLEAR
        - call LISTE

    LISTE:
        - redraw omain PageList

    SELECT:
        - redraw omain PageProduit <selected>

    ADD:
        - addBasket <selected>
        - redraw obasket Basket <baskets>

    CLEAR:
        - set:
            key: baskets
            value: []
        - redraw obasket Basket <baskets>
    """

    # more specific keywords language :

    def addBasket(self,ref):
        self.state["baskets"].append( ref )



class PageList(Tag.div):
    def init(self):
        self <= Tag.h1("Produits")
        for ref,produit in PRODUITS.items():
            d=Tag.div(_style="border:1px dotted black;display:inline-block;width:100px;height:100px")
            d<=Tag.h3(produit.name)
            d<=Tag.button("Voir", value=ref, _onclick = lambda o: self.root.next('SELECT',selected=o.value) )
            d<=Tag.button("Add", value=ref,_onclick = lambda o: self.root.next('ADD',selected=o.value) )
            self <= d

class PageProduit(Tag.div):
    def init(self,ref):
        produit = PRODUITS[ref]

        b=Tag.button("back", _onclick = lambda o: self.root.next('LISTE') )
        self <= Tag.h1(b+f"Produits > {produit.name}")
        self <= Tag.h3(f"Price: {produit.price}€")
        self <= Tag.button("Add", _onclick = lambda o: self.root.next('ADD',selected=ref) )

class Basket(Tag.div):
    def init(self,liste:list):
        if liste:
            somme=0
            for ref in liste:
                produit = PRODUITS[ref]
                self <= Tag.li( f"{produit.name}: {produit.price}€" )
                somme+=produit.price
            self <= Tag.b(f"Total: {somme}€")
            self <= Tag.button("clear", _onclick = lambda o: self.root.next('CLEAR') )
        else:
            self <= "vide"


class App(Tag.body):
    def init(self):
        # init objects
        self.omain = Tag.div()
        self.obasket = Tag.div(_style="position:fixed;top:0px;right:0px;background:yellow")

        # create layout
        self <= self.omain + self.obasket

        # start bpm
        self.bpm=MyBPM({} , [PageList,PageProduit,Basket] )
        self.next("START")

    def next(self,node,**params):
        self.bpm( node,**params)

        # draw objects managed in bpm
        self.omain.set( self.bpm.draw("omain") )
        self.obasket.set( self.bpm.draw("obasket") )

        # just displaying some infos
        print(":::: state",self.bpm.state)


#=================================================================================
from htag.runners import DevApp as Runner
# from htag.runners import BrowserHTTP as Runner
# from htag.runners import ChromeApp as Runner

import logging
logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

logging.getLogger("htag.tag").setLevel( logging.ERROR )
logging.getLogger("htag.render").setLevel( logging.ERROR )
logging.getLogger("uvicorn.error").setLevel( logging.ERROR )
logging.getLogger("asyncio").setLevel( logging.ERROR )

app=Runner(App)
if __name__=="__main__":
    app.run()
