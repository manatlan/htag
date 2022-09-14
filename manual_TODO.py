from htag import Tag
from htag.render import HRenderer

class App(Tag.div):
    def init(self,m="default"):
        self <= m
        self <= Tag.span("world")

s=App()
print(s)

hr=HRenderer(App,"")
print(hr.tag)

def gen():
    for i in range(3):
        yield i
d=Tag.div()
d.add( gen() )
assert str(d) == "<div>012</div>"

