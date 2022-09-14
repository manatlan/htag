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

