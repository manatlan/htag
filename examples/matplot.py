# -*- coding: utf-8 -*-

from htag import Tag
import io,base64,random
import matplotlib.pyplot as plt

class TagPlot(Tag.span):
    def init(self,plt):
        self["style"]="display:inline-block"
        with io.StringIO() as fid:
            plt.savefig(fid,format='svg',bbox_inches='tight')
            self <= fid.getvalue()

class App(Tag):
    def init(self):
        self.main = Tag.div()
        self.liste=[1, 2, 5, 4]
        
        # create the layout
        self <= Tag.h3("Matplotlib test" + Tag.button("Add",_onclick=self.add_random))
        self <= self.main
        
        self.redraw_svg()

    def add_random(self,o):
        self.liste.append( random.randint(1,6))
        self.redraw_svg()

    def redraw_svg(self):
        plt.ylabel('some numbers')
        plt.xlabel('size of the liste')
        plt.plot(self.liste)
        
        self.main.clear()
        self.main <= TagPlot(plt)

if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP(App).run()
