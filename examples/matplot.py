# -*- coding: utf-8 -*-

from htag import Tag
import matplotlib.pyplot as plt
import io,base64,random

class App(Tag):
    def init(self):
        self.img = Tag.img()
        self.liste=[1, 2, 5, 4]
        
        # create the layout
        self <= Tag.h3("Matplotlib test") + self.img
        self <= Tag.button("Add",_onclick=self.add_random)
        
        self.redraw_svg()

    def add_random(self,o):
        self.liste.append( random.randint(1,6))
        self.redraw_svg()

    def redraw_svg(self):
        plt.plot(self.liste)
        plt.ylabel('some numbers')
        
        data=io.BytesIO()
        plt.savefig(data)
        data.seek(0)
        
        self.img["src"]=u'data:image/svg;base64,'+base64.b64encode(data.read()).decode()


if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP(App).run()
