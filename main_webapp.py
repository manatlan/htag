from htag import Tag, WebApp

class Hello(Tag.App):
    def init(self):
        self += "Hello World from WebApp.run!"
        self += Tag.button("Click me!", _onclick=self.click)
        self.count = 0
        
    def click(self, ev):
        self.count += 1
        self += f" Clicked {self.count} times"

if __name__ == "__main__":
    WebApp(Hello, debug=True).run(port=8001)
