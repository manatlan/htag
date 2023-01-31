class App(Tag.div):
    imports=[]

    def init(self):
        self.call.drawui()
        
    def drawui(self):
        for i in range(3):
            yield
            self <= Tag.my_tag(f"content{i}")
            self.call.check( b"self.innerHTML" )
        yield
        self.clear()
        self <= Tag.button("exit",_onclick = lambda o: self.exit())        

    def check(self,innerhtml):
        assert self.innerHTML == innerhtml



class App(Tag.div):
    imports=[]

    def init(self):
        self.call.streamui()
        
    def streamui(self):
        for i in range(3):
            yield Tag.my_tag(f"content{i}")
            self.call.check( b"self.innerHTML" )
        yield
        self.clear()
        self <= Tag.button("exit",_onclick = lambda o: self.exit())        

    def check(self,innerhtml):
        assert self.innerHTML == innerhtml
