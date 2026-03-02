from htag import Tag

class App(Tag.App):
    def init(self):
        self += Tag.h1("Hello Toto!", _style="color: red;")
        self += Tag.button("Click me", _onclick=self.do_click)
        self.msg = Tag.div()
        self += self.msg
        
    def do_click(self, o):
        self.msg += "Clicked! "

app=App