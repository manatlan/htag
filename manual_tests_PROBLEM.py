from htag import Tag
import htbulma as b

class Tabs(Tag.div): # New version (NOT htag optimized ;-()

    def __init__(self,**a):
        super().__init__(**a)
        self.__tabs={}
        self.__selected = None

    def addTab(self,name,content):
        self.__tabs[name] = content
        if self.__selected is None:
            self.__selected=name
        self._render()

    def _render(self):
        self.clear()

        ll=[]
        for k,v in self.__tabs.items():
            self <= Tag.button(k,value=k,_onclick= self._setselected,_style="background:red" if self.__selected==k else "" )

        d=Tag.div()
        if self.__selected:
            d.add( self.__tabs[ self.__selected ], True )
        self <= d

    @property
    def selected(self):
        return self.__selected

    @selected.setter
    def selected(self, v):
        self.__selected =v
        self._render()

    def _setselected(self,obj):
        self.__selected = obj.value
        self._render()

class App(Tag.body):

  def init(self):

    obj=Tag.div("hihi")

    tab = Tabs()
    tab.addTab("Tab 1", obj )
    tab.addTab("Tab 2", "hello2" )

    self <= tab


from htag.runners import *
app=DevApp( App )

if __name__=="__main__":
    # import logging
    # logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    app.run()
