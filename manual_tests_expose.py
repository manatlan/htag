#!./venv/bin/python3
from htag import Tag,expose
Tag.STRICT_MODE=True

class App(Tag.div):
    def init(self):
        # the old bind (for js interact)
        self+=Tag.button("test1",_onclick=self.bind.python(3,"[1]"))

        # the new bind (for js interact)
        self+=Tag.button("test2",_onclick=self.bind(self.python,4,b"[2]"))
        
        # create a js caller (only old bind)
        #~ self.js = "self.python=function(_) {%s}" % self.bind.python(b"...arguments")
        #~ self+=Tag.button("test",_onclick='self.python(5,"x")')

        # ^^ REPLACE something like that ^^
        self+=Tag.button("test3",_onclick='this.parentNode.python(6,"[3]")')

    @expose # only needed for button 'test3'
    def python(self,nb,data):
        self+= nb * str(data)
        
from htag.runners import BrowserHTTP as Runner

app=Runner( App )
if __name__=="__main__":
    app.run()
        
        