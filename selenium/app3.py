import sys,os; sys.path.insert(0,os.path.join( os.path.dirname(__file__),".."))
import hclient
#################################################################################
from htag import Tag

class App(Tag.div):
    """ Stream UI """

    imports=[]

    def init(self):
        self.call.streamui()

    def streamui(self):
        for i in range(3):
            yield Tag.my_tag(f"content{i}")
            self.call.check( b"self.innerHTML" )
        yield
        self.clear()
        self <= Tag.button("exit",_onclick = lambda o: self.exit())

    def check(self,innerhtml):
        assert self.innerHTML == innerhtml

#################################################################################

def tests(client:hclient.HClient):
    assert "App" in client.title
    client.wait(2)
    client.click('//button[text()="exit"]')
    return True


if __name__=="__main__":
    # hclient.run( App, "BrowserHTTP")
    hclient.test( App, "BrowserHTTP", tests)
