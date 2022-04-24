from htag import Tag
import htbulma as b

class Star1(Tag.div): # it's a component ;-)
    """ rendering lately """

    def init(self,value=0):
        self.value=value

    def inc(self,v):
        self.value+=v

    def render(self): # <- ensure dynamic rendering
        self <= b.Button( "-", _onclick = lambda o: self.inc(-1), _class="is-small" )
        self <= b.Button( "+", _onclick = lambda o: self.inc(1) , _class="is-small" )
        self <= "⭐"*self.value

class Star2(Tag.div): # it's a component ;-)
    """ rendering immediatly """

    def init(self,value=0):
        self.value=value
        self <= b.Button( "-", _onclick = self.bind.inc(-1), _class="is-small" )
        self <= b.Button( "+", _onclick = self.bind.inc(1) , _class="is-small" )
        # self <= b.Button( "-", _onclick = lambda o: self.inc(-1), _class="is-small" )
        # self <= b.Button( "+", _onclick = lambda o: self.inc(1) , _class="is-small" )

        self.content = Tag.span( "⭐"*self.value )
        self <= self.content

    @Tag.NoRender
    def inc(self,v):
        self.value+=v
        self.content.set( "⭐"*self.value )



class App(Tag.body):
  statics = Tag.style("""html {
    user-select: none;
    -ms-touch-action: manipulation;
    touch-action: manipulation;
}""")

  def init(self):
    self._mbox = b.MBox(self)

    nav = b.Nav("My App")
    nav.addEntry("entry 1", lambda: self._mbox.show( "You choose 1" ) )
    nav.addEntry("entry 2", lambda: self._mbox.show( "You choose 2" ) )

    tab = b.Tabs()
    tab.addTab("Tab 1", Tag.b("Set star1s") + Star1(12) )
    tab.addTab("Tab 2", Tag.b("Set star2s") + Star2(12) )

    self <= nav + b.Section( tab )


if __name__=="__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    app=App()

    from htag.runners import BrowserHTTP
    BrowserHTTP( app ).run()
