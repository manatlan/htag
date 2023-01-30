import sys,os; sys.path.insert(0,os.path.join( os.path.dirname(__file__),".."))
from common import HClient
#################################################################################
from htag import Tag

class App(Tag.body):
    def init(self):
        def say_hello(o):
            self <= Tag.li("hello")
        self<= Tag.button("click",_onclick = say_hello)
        self<= Tag.button("exit",_onclick = lambda o: self.exit())

#################################################################################

def tests(client:HClient):
    assert "App" in client.title

    client.click('//button[text()="click"]')
    client.click('//button[text()="click"]')
    client.click('//button[text()="click"]')

    assert len(client.find('//li'))==3

    client.click('//button[text()="exit"]')
    return True
