import sys
from htag import Tag # the only thing you'll need ;-)


class Gui2(Tag.body):

    def init(self):
        self.valueC=0
        self.valueF=0

    def render(self):
        self.clear()
        self <= Tag.div( Tag.Input( _value=self.valueC, _onchange=self.bind.changeC(b"this.value") ) +"C" )
        self <= Tag.div( Tag.Input( _value=self.valueF, _onchange=self.bind.changeF(b"this.value") ) +"F")

    def changeC(self,v):
        self.valueC=float(v)
        self.valueF=(self.valueC*9/5) - 32

    def changeF(self,v):
        self.valueF=float(v)
        self.valueC=(self.valueF-32) *(5/9)



App=Gui2
if __name__=="__main__":
    # and execute it in a pywebview instance
    from htag.runners import *
    PyWebWiew( Gui2 ).run()

    # here is another runner, in a simple browser (thru ajax calls)
    # BrowserHTTP( Page ).run()
