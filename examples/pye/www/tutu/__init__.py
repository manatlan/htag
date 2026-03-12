from htag import Tag

class Tutu(Tag.App):
    def init(self):
        self += Tag.h1("Hello tutu!!!", _style="color: blue;")
        self += Tag.button("Click me", _onclick=self.do_click)
        self.msg = Tag.div()
        self += self.msg
        
    def do_click(self, o):
        self.msg += Tag.p("tutu Clicked! ")

App=Tutu
