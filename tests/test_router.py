import pytest
from htag import Tag, Router

class Page1(Tag.div):
    def init(self) -> None:
        self.text = "Page1"

class Page2(Tag.div):
    def init(self, name: str) -> None:
        self.text = f"Hello {name}"

def test_router_basics():
    router = Router()
    router.add_route("/p1", Page1)
    router.add_route("/p/:name", Page2)
    
    # Internal navigation (no event needed for unit testing)
    router._navigate_to("/p1")
    assert len(router.childs) == 1
    assert isinstance(router.childs[0], Page1)
    assert router.childs[0].text == "Page1"
    
    # Switch page
    router._navigate_to("/p/World")
    assert len(router.childs) == 1
    assert isinstance(router.childs[0], Page2)
    assert router.childs[0].text == "Hello World"
    
def test_router_not_found():
    router = Router()
    router.add_route("/", Page1)
    
    router._navigate_to("/unknown")
    assert len(router.childs) == 1
    assert "404" in str(router.childs[0])
    assert "Page not found" in str(router.childs[0])
    
    # Custom 404
    class My404(Tag.div):
        def init(self) -> None:
            self.text = "Oups!"
            
    router.set_not_found(My404)
    router._navigate_to("/wrong")
    assert "Oups!" in str(router.childs[0])

def test_router_regex_matching():
    router = Router()
    # Ensure it doesn't match partially
    router.add_route("/tasks", Page1)
    
    router._navigate_to("/tasks/12")
    assert "404" in str(router.childs[0]) 

def test_router_complex_params():
    router = Router()
    
    class MultiParam(Tag.div):
        def init(self, category, id):
            self.category = category
            self.id = id
            
    router.add_route("/posts/:category/:id", MultiParam)
    router._navigate_to("/posts/tech/42")
    
    assert isinstance(router.childs[0], MultiParam)
    assert router.childs[0].category == "tech"
    assert router.childs[0].id == "42"

def test_router_initial_route_event():
    router = Router()
    router.add_route("/", Page1)
    
    # Simulate htag_event from JS
    router._on_init_route(type('Event', (object,), {'value': {'hash': '#/'}})())
    assert isinstance(router.childs[0], Page1)

def test_router_path_is_reactive_state():
    """router.path should be a State, enabling reactive tab styling."""
    from htag.core import State
    router = Router()
    router.add_route("/", Page1)
    router.add_route("/hello/:name", Page2)
    
    # path is a State instance
    assert isinstance(router.path, State)
    
    # Initially empty
    assert router.path == ""
    
    # After navigation, path reflects the route
    router._navigate_to("/")
    assert router.path == "/"
    
    router._navigate_to("/hello/World")
    assert router.path == "/hello/World"
    
    # Comparison operators work (essential for lambda: "active" if router.path == "/" else "")
    assert router.path != "/"
    assert router.path == "/hello/World"
