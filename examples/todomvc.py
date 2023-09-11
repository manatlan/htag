# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
# see https://metaperl.github.io/pure-python-web-development/todomvc.html

from htag import Tag
from dataclasses import dataclass

@dataclass
class Todo:
    txt: str
    done: bool=False

class MyTodoListTag(Tag.div):
    statics = "label {display:block;cursor:pointer;padding:4px}"

    def init(self):
        # init the list
        self._list = []

        # and make a 1st draw
        self.redraw()

    def redraw(self):
        # clear content
        self.clear()

        if self._list:
            # if there are todos

            def statechanged(o):
                # toggle boolean, using the ref of the instance object 'o'
                o.ref.done = not o.ref.done

                # force a redraw (to keep state sync)
                self.redraw()

            # we draw the todos with checkboxes
            for i in self._list:
                self += Tag.label([
                    # create a 'ref' attribut on the instance of the input, for the event needs
                    Tag.input(ref=i,_type="checkbox",_checked=i.done,_onchange=statechanged),
                    i.txt
                ])
        else:
            # if no todos
            self += Tag.label("nothing to do ;-)")

    def addtodo(self,txt:str):
        txt=txt.strip()
        if txt:
            # if content, add as toto in our ref list
            self._list.append( Todo(txt) )

            # and force a redraw
            self.redraw()


class App(Tag.body):
    statics="body {background:#EEE;}"

    # just to declare that this component will use others components
    # (so this one can declare 'statics' from others)
    imports=[MyTodoListTag,]    # not needed IRL ;-)

    def init(self):
        # create an instance of the class 'MyTodoListTag', to manage the list
        olist=MyTodoListTag()

        # create a form to be able to add todo, and bind submit event on addtodo method
        oform = Tag.form( _onsubmit=olist.bind.addtodo(b"this.q.value") + "return false" )
        oform += Tag.input( _name="q", _type="search", _placeholder="a todo ?")
        oform += Tag.Button("add")

        # draw ui
        self += Tag.h3("Todo list") + oform + olist



#=================================================================================
# the runner part
#=================================================================================
from htag.runners import BrowserHTTP as Runner
# from htag.runners import DevApp as Runner
# from htag.runners import PyWebView as Runner
# from htag.runners import BrowserStarletteHTTP as Runner
# from htag.runners import BrowserStarletteWS as Runner
# from htag.runners import BrowserTornadoHTTP as Runner
# from htag.runners import AndroidApp as Runner
# from htag.runners import ChromeApp as Runner
# from htag.runners import WinApp as Runner

app=Runner(App)
if __name__=="__main__":
    app.run()
