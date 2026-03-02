from htag import Tag

class App(Tag.App):
    def init(self):
        self += Tag.h1("Hello tutu!", _style="color: blue;")
        self += Tag.button("Click me", _onclick=self.do_click)
        self.msg = Tag.div()
        self += self.msg
        
    def do_click(self, o):
        self.msg += "tutu Clicked! "

app=App
