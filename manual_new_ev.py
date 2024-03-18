#!./venv/bin/python3
# -*- coding: utf-8 -*-

from htag import Tag
import asyncio,time

class App(Tag.body):

    def init(self, name="vide"):
        self["style"]="background:#FFE;"
        self <= "Hello "+name
        self <= Tag.button("add content1 (new)", _onclick=self.add_content1)
        self <= Tag.button("add content2 (new)", _onclick=self.add_content2)
        self <= Tag.button("add content (old)", _onclick=self.bind.add_content1(None))

    def add_content1(self,o):           # old <= 0.91 : o is the caller_object, and event is in o.event
        self <= f"X {o.innerHTML}"
    def add_content2(self,ev):          # new >= 0.100 : ev is a real event (ev.target is the caller_object)
        self <= f"X {ev.target.innerHTML}"




from htag.runners import Runner,HTTPResponse
app=Runner(App,reload=False,debug=True)

if __name__=="__main__":
    app.run()
