# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag
import io,base64,random
import matplotlib.pyplot as plt

class TagPlot(Tag.span):
    def init(self,plt):
        self["style"]="display:inline-block"
        with io.StringIO() as fid:
            plt.savefig(fid,format='svg',bbox_inches='tight')
            self <= fid.getvalue()

class App(Tag.body):
    def init(self):
        self.content = Tag.div()
        
        # create the layout
        self += Tag.h2("MatPlotLib " + Tag.button("Random",_onclick=self.redraw_plt))
        self += self.content
        
        self.redraw_plt()

    def redraw_plt(self,obj=None):
        plt.clf()
        plt.ylabel('Some numbers')
        plt.xlabel('Size of my list')
        my_list=[random.randint(1,10) for i in range(random.randint(20,50))]
        plt.plot( my_list )
        
        self.content.clear()
        self.content += Tag.div(f"My list: {my_list}")
        self.content += TagPlot(plt)

from htag.runners import BrowserHTTP as Runner
app=Runner(App)
if __name__=="__main__":
    app.run()
