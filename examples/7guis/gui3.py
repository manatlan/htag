import sys
from htag import Tag # the only thing you'll need ;-)


class Gui3(Tag.body):

    def init(self):
        self.selected = "One Way"

    def render(self):
        options = [Tag.option(i,_selected=(self.selected==i)) for i in ["One Way","Return Flight"]]

        self.clear()
        self <= Tag.Select( options, _onchange=self.bind.setSelected(b"this.value") )
        self <= Tag.input(_type="date")
        self <= Tag.input(_type="date",_disabled=self.selected=="One Way")

    def setSelected(self,v):
        self.selected = v




App=Gui3
if __name__=="__main__":
    # and execute it in a pywebview instance
    from htag.runners import *
    PyWebWiew( Gui3 ).run()

    # here is another runner, in a simple browser (thru ajax calls)
    # BrowserHTTP( Page ).run()
