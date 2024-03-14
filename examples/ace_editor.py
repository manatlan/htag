import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag
import html

class Ed(Tag.div):
    """ A class which embed the ace editor (python syntax) """

    statics = [
        Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.14/ace.js"),
        Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.14/mode-python.js"),
        Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.14/theme-cobalt.js"),
        Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.14/ext-searchbox.js"),
        Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.14/ext-language_tools.js"),
    ]

    def __init__(self,value,width="100%",height="100%",mode="python",onsave=None):
        self.value = value
        super().__init__(_style="width:%s;height:%s;" % (width,height))
        placeholder="myed%s" % id(self)

        oed= Tag.div(self.value,_style="width:100%;height:100%;min-height:20px;")
        self <= oed
        self.onsave=onsave

        self.js = """
tag.ed=ace.edit( "%s" );
tag.ed.setTheme("ace/theme/cobalt");
tag.ed.session.setMode("ace/mode/%s");
tag.ed.session.setUseWrapMode(false);
tag.ed.setOptions({"fontSize": "12pt"});
tag.ed.setBehavioursEnabled(false);
tag.ed.session.setUseWorker(false);
tag.ed.getSession().setUseSoftTabs(true);

function commandSave () {%s}

tag.ed.commands.addCommand({
    name: "commandSave",
    bindKey: {"win": "Ctrl-S",  "mac": "Command-S"},
    readOnly: "True",
    exec: commandSave,
})
""" % (id(oed),mode, self.bind._save( b"tag.ed.getValue()"))

    def _save(self,value):
        self.value = value
        if self.onsave: self.onsave(self)


class App(Tag.body):
    """ Using a component which embed the ace editor """
    statics=[Tag.style("""
html, body {width:100%;height:100%;margin:0px}
""")]
    imports=Ed  # IRL, this line is not needed

    def init(self):
        self.e1 = Ed("text1", onsave=self.maj)
        self.e2 = Ed("text2", onsave=self.maj)
        self <= Tag.div(
                self.e1+self.e2,
                _style="height:100px;display:flex;gap:4px;"
            )
        self.txt=Tag.pre("Press CTRL+S in each Editor")
        self <= self.txt

    def maj(self,o):
        self.txt.clear( f"{html.escape(repr(o))} saved -> '{o.value}'" )


from htag.runners import DevApp as Runner           # need starlette+uvicorn !!!
#from htag.runners import BrowserHTTP as Runner
app=Runner(App)
if __name__=="__main__":
    app.run()
