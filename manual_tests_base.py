#!./venv/bin/python3
from htag import Tag,Runner

class App(Tag.body):
    def init(self):
        self.ph=Tag.div()   #placeholder

        self <= Tag.button("nimp", _onclick=self.print)
        self <= Tag.input( _onkeyup=self.print)
        self <= self.ph

    def print(self,o):
        self.ph.clear(str(o.event))


if __name__ == "__main__":
    app=Runner( App )
    
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.INFO)
    logging.getLogger("htag.tag").setLevel( logging.INFO )
    app.run()
