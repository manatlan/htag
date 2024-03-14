#!./venv/bin/python3
from htag import Tag # the only thing you'll need ;-)

class Nimp(Tag.div):
    def init(self):
        # !!! previous3 will not be saved in '/tmp/AEFFFF.json' !!!
        # (it's not the main/managed tag (which is Page), so it's an inner dict)
        self.state["previous3"]=self.state.get("previous3","") + "!"
        self.clear( self.state["previous3"] )


class Page(Tag.body):
    def init(self):
        self.session["previous"]=self.session.get("previous","") + "!"
        self.state["previous2"]=self.state.get("previous2","") + "!"

        self+=Tag.div( self.session["previous"] )
        self+=Tag.div( self.state["previous2"] )
        self+=Nimp()


# from htag.runners import DevApp as Runner
from htag.runners import ChromeApp as Runner
# from htag.runners import WinApp as Runner
# from htag.runners import BrowserTornadoHTTP as Runner
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import BrowserHTTP as Runner
# from htag.runners import AndroidApp as Runner
# from htag.runners import PyWebView as Runner

app=Runner( Page , file="/tmp/AEFFFF.json")
if __name__ == "__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.ERROR)
    logging.getLogger("htag.tag").setLevel( logging.ERROR )
    # app.run()
    app.run()
