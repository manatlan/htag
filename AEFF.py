from htag import Tag
import htbulma as b

class Star(Tag.div): # it's a component ;-)

    def init(self,value=0):
        self.value=value

    def more(self,o): self.value+=1
    def less(self,o): self.value-=1

    def render(self): # <- ensure dynamic rendering
        self <= b.Button( "-", _onclick = self.less, _class="is-small" )
        self <= b.Button( "+", _onclick = self.more, _class="is-small" )
        self <= "⭐"*self.value


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

    s = Star(12)

    tab = b.Tabs()
    tab.addTab("Tab 1", Tag.b("Set stars") + s )
    tab.addTab("Tab 2", b.Box("Page 2") )

    self <= nav + b.Section( tab )


if __name__=="__main__":

  app=App()

  from htag.runners import BrowserHTTP
  BrowserHTTP( app ).run()
