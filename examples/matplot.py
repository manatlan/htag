# -*- coding: utf-8 -*-

from htag import Tag
import io,base64,random
import matplotlib.pyplot as plt

class App(Tag):
    def init(self):
        self.img = Tag.svg(_viewBox="0 0 1000 1500")
        self.liste=[1, 2, 5, 4]
        
        # create the layout
        self <= Tag.h3("Matplotlib test" + Tag.button("Add",_onclick=self.add_random))
        self <= self.img
        
        self.redraw_svg()

    def add_random(self,o):
        self.liste.append( random.randint(1,6))
        self.redraw_svg()

    def redraw_svg(self):
        plt.plot(self.liste)
        plt.ylabel('some numbers')
        plt.xlabel('size of the liste')
        
        with io.StringIO() as fid:
            plt.savefig(fid,format='svg')
            self.img.set( fid.getvalue() )

if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP(App).run()
