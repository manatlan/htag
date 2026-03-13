from htag import Tag

class Tata(Tag.App):
    _parano_ = True
    def init(self):
        self += Tag.h1("Hello tata ! (parano)", _style="color: green;")
        self += Tag.button("Click me", _onclick=self.do_click)
        self.msg = Tag.div()
        self += self.msg

    def do_click(self, o):
        self.msg += "tata Clicked! "

App=Tata