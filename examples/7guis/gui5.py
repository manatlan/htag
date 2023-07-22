import sys
from htag import Tag # the only thing you'll need ;-)


class Gui5(Tag.body):
    """ https://eugenkiss.github.io/7guis/tasks#crud """

    def init(self):
        self.db=["albert","franz","fred"]
        self.selected=None
        self.filter=""
        self.name = ""

    def render(self):
        options = [Tag.option(i,_value=idx,_selected=idx==self.selected) for idx,i in enumerate(self.db) if self.filter in i]

        self <= Tag.Input( _value=self.filter, _onchange=self.bind.changeFilter(b"this.value"),_placeholder="filter" )
        self <= Tag.br()
        self <= Tag.select( options, _size=10, _onchange=self.bind.setSelected(b"this.value") ,_style="width:80px")
        self <= Tag.Input( _value=self.name, _onchange=self.bind.changeName(b"this.value") )
        self <= Tag.hr()
        self <= Tag.Button( "create", _onclick=self.bind.create() )
        self <= Tag.Button( "delete", _onclick=self.bind.delete() )
        self <= Tag.Button( "update", _onclick=self.bind.update() )

    def setSelected(self,v):
        self.selected = int(v)
        self.name = self.db[self.selected]

    def changeFilter(self,v):
        self.filter = v

    def changeName(self,v):
        self.name = v

    def create(self):
        self.db.append(self.name)

    def delete(self):
        if self.selected is not None:
            del self.db[self.selected]
            self.selected=None

    def update(self):
        if self.selected is not None:
            self.db[self.selected] = self.name


App=Gui5
if __name__=="__main__":
    # and execute it in a pywebview instance
    from htag.runners import *
    PyWebWiew( Gui5 ).run()

    # here is another runner, in a simple browser (thru ajax calls)
    # BrowserHTTP( Page ).run()
