from htag import Tag, ChromeApp, Router

class HomePage(Tag.div):
    def init(self) -> None:
        Tag.h1("Home")
        Tag.p("Welcome to this simple SPA demo.")

class Page1(Tag.div):
    def init(self) -> None:
        Tag.h1("Page 1")
        Tag.p("This is page 1 content.")

class HelloPage(Tag.div):
    def init(self, name: str) -> None:
        Tag.h1(f"Hello {name}!")

class App(Tag.App):
    statics = [Tag.style("""
        body { font-family: system-ui; margin: 0; background: #1a1a2e; color: #e0e0e0; }
        nav { display: flex; gap: 0; background: #16213e; border-bottom: 2px solid #0f3460; }
        nav a { padding: 12px 24px; text-decoration: none; color: #8899aa;
                transition: all 0.2s; border-bottom: 2px solid transparent; }
        nav a:hover { color: #e94560; }
        nav a.active { color: #e94560; border-bottom-color: #e94560; font-weight: bold; }
        .content { padding: 32px; }
    """)]

    def init(self) -> None:
        self.router = Router()
        self.router.add_route("/", HomePage)
        self.router.add_route("/p1", Page1)
        self.router.add_route("/hello/:name", HelloPage)

        # Navigation with reactive "active" class thanks to router.path (State)
        with Tag.nav():
            Tag.a("Home",    _href="#/",            _class=lambda: "active" if self.router.path == "/" else "")
            Tag.a("Page 1",  _href="#/p1",          _class=lambda: "active" if self.router.path == "/p1" else "")
            Tag.a("Hello",   _href="#/hello/World",  _class=lambda: "active" if self.router.path == "/hello/World" else "")

        with Tag.div(_class="content"):
            self <= self.router

if __name__ == "__main__":
    ChromeApp(App).run(reload=True, port=0)
