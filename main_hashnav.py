from htag import Tag, prevent
import logging


class App(Tag.App):
    def init(self):

        self._onhashchange = self.on_hash

        with Tag.div():
            Tag.a("[P1]", _href="#page1")
            Tag.a("[P2]", _href="#page2")

    def on_hash(self, ev):
        self <= Tag.div("hash changed to", ev.newURL)

if __name__ == "__main__":
    from htag import ChromeApp   
    ChromeApp(App).run()
