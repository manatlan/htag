#!./venv/bin/python3
from htag import Tag
import htbulma as b

class Star1(Tag.div): # it's a component ;-)
    """ rendering lately (using render (called before __str__))

        it's simpler ... but event/action shouldn't try to draw something, coz render will rebuild all at each time
    """

    def init(self,value=0):
        self.value=value

    def inc(self,v):
        self.value+=v

    def render(self): # <- ensure dynamic rendering
        self.clear()
        self <= b.Button( "-", _onclick = lambda o: self.inc(-1), _class="is-small" )
        self <= b.Button( "+", _onclick = lambda o: self.inc(+1), _class="is-small" )
        self <= "⭐"*self.value

class Star2(Tag.div): # it's a component ;-)
    """ rendering immediatly (each event does the rendering)

        it's less simple ... but event/action should redraw something !

    """

    def init(self,value=0):
        self.value=value
        self <= b.Button( "-", _onclick = lambda o: self.inc(-1), _class="is-small" )
        self <= b.Button( "+", _onclick = lambda o: self.inc(+1), _class="is-small" )

        self.content = Tag.span( "⭐"*self.value )
        self <= self.content

    def inc(self,v):
        self.value+=v
        self.content.clear( "⭐"*self.value )



class App(Tag.body):

  def init(self):
    self._s = b.Service(self)

    nav = b.Nav("My App")
    nav.addEntry("entry 1", lambda: self._s.alert( "You choose 1" ) )
    nav.addEntry("entry 2", lambda: self._s.alert( "You choose 2" ) )

    tab = b.Tabs()
    tab.addTab("Tab 1", Tag.b("Set star1s") + Star1(12) )
    tab.addTab("Tab 2", Tag.b("Set star2s") + Star2(12) )

    self <= nav + b.Section( tab )


if __name__=="__main__":
    # import logging
    # logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    from htag.runners import *
    BrowserStarletteWS( App ).run()
