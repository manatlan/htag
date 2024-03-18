#!./venv/bin/python3
# -*- coding: utf-8 -*-

from htag import Tag

class App(Tag.body):

    def init(self, name="vide"):
        self["style"]="background:#FFE;"
        self <= "Hello "+name
        self <= Tag.button("add content (very old)", _onclick=self.bind.add_content_old())
        self <= Tag.button("add content1 (old)", _onclick=self.add_content1)
        self <= Tag.button("add content2 (new)", _onclick=self.add_content2)

    def add_content_old(self):
        self <= Tag.li(f"OLD <b>EVENT:</b>{self.event}")

    def add_content1(self,o):           # old <= 0.91 : o is the caller_object, and event is in o.event
        self <= Tag.li(f"{o.innerHTML} <b>EVENT:</b>{o.event}")

    def add_content2(self,ev):          # new >= 0.100 : ev is a real event (ev.target is the caller_object)
        self <= Tag.li(f"{ev.target.innerHTML} <b>EVENT:</b>{ev}")


from htag.runners import Runner
app=Runner(App,debug=True)

if __name__=="__main__":
    app.run()
