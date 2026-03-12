from htag import Tag

class Titi(Tag.App):
    def init(self):
        self += Tag.h1("Hello titi !", _style="color: green;")
        self += Tag.button("Click me", _onclick=self.do_click)
        self.msg = Tag.div()
        self += self.msg
        
    def do_click(self, o):
        self.msg += "titi Clicked! "

App=Titi
# print("suis un script")