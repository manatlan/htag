from htag import Tag

class Tutu2(Tag.App):
    def init(self):
        self += Tag.h1("Hello tutu2", _style="color: violet;")
        self += Tag.button("Click me", _onclick=self.do_click)
        self.msg = Tag.div()
        self += self.msg
        
    def do_click(self, o):
        self.msg += "tutu2 Clicked! "

app=Tutu2
