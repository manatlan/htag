from htag import Tag, ChromeApp, Router

class HomePage(Tag.div):
    def init(self) -> None:
        Tag.h1("Home")
        Tag.p("Welcome to this simple SPA demo.")
        Tag.a("Go to Page 1", _href="#/p1")
        Tag.br()
        Tag.a("Go to Hello/World", _href="#/hello/World")

class Page1(Tag.div):
    def init(self) -> None:
        Tag.h1("Page 1")
        Tag.a("Back Home", _href="#/")

class HelloPage(Tag.div):
    def init(self, name: str) -> None:
        Tag.h1(f"Hello {name}!")
        Tag.a("Back Home", _href="#/")

class App(Tag.App):
    def init(self) -> None:
        self.router = Router()
        
        self.router.add_route("/", HomePage)
        self.router.add_route("/p1", Page1)
        self.router.add_route("/hello/:name", HelloPage)
        
        self += self.router

if __name__ == "__main__":
    ChromeApp(App).run(reload=True, port=0)
