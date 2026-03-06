from htag import Tag, prevent
import logging


class MyApp(Tag.App):
    def init(self):
        b = Tag.button("add", _onclick=self.onclick, _oncontextmenu=self.onmenu, _style="color:green")
        b.a_var=42
        self <= b

    def onclick(self, event):
        self <= Tag.div(f"hello {event.target.a_var} {event}")
        self <= "hello"
        yield
        self <= "hello2"

        event.target.a_var += 1
        event.target._style = "color:red"
        event.target <= Tag.span("added")
        event.target.call_js("console.log('Button clicked!')")

    @prevent
    def onmenu(self, event):
        event.target <= Tag.span("menu")

if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(MyApp).run()
