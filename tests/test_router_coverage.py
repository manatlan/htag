import pytest
from htag import Tag, Router

class Page(Tag.div):
    def init(self): self.text = "Page"

def test_router_on_hash_change_variants():
    router = Router()
    router.add_route("/p", Page)
    
    # Test line 132-140: hashchange with newURL
    class MockEvent:
        def __init__(self, url): self.newURL = url
        
    router._on_hash_change(MockEvent("http://localhost/#/p"))
    assert router.path == "/p"
    
    # Test line 137: fallback to / (already on /p, so it should clear and hit / which is 404)
    router._on_hash_change(MockEvent("http://localhost/"))
    assert router.path == "/"
    assert "404" in str(router.childs[0])

def test_router_init_route_legacy_event():
    router = Router()
    router.add_route("/home", Page)
    
    # Test line 119-120: legacy direct hash property
    class LegacyEvent:
        hash = "#/home"
    router._on_init_route(LegacyEvent())
    assert router.path == "/home"

def test_router_redundant_navigation():
    router = Router()
    router.add_route("/p", Page)
    router._navigate_to("/p")
    
    # Snapshot children count
    count = len(router.childs)
    
    # Test line 146: return if same path
    router._navigate_to("/p") 
    assert len(router.childs) == count

def test_router_navigate_js():
    router = Router()
    # Test line 192: call_js
    router.navigate("/target")
    # Verify the call_js was recorded in the internal __js_calls list of the Tag
    assert any("window.location.hash='/target'" in js for js in router._consume_js_calls())

def test_router_on_mount_wires_events():
    """Cover on_mount(): wires hashchange, init_route event, and call_js."""
    class App(Tag.App):
        def init(self):
            self.router = Router()
            self.router.add_route("/", Page)
            self <= self.router

    app = App()
    # on_mount should have wired onhashchange on root
    assert app["onhashchange"] is not None
    # on_mount should have wired oninit_route on the router
    assert app.router["oninit_route"] is not None
    # on_mount should have queued a call_js for initial hash resolution
    js_calls = app.router._consume_js_calls()
    assert any("init_route" in js for js in js_calls)

def test_router_init_route_hash_without_slash():
    """Cover L129: hash value without leading slash (e.g. '#home' instead of '#/home')."""
    router = Router()
    router.add_route("/home", Page)

    class MockEvent:
        hash = "#home"  # no leading slash
    router._on_init_route(MockEvent())
    assert router.path == "/home"

def test_router_hashchange_without_slash():
    """Cover L141: newURL hash segment without leading slash."""
    router = Router()
    router.add_route("/p", Page)

    class MockEvent:
        newURL = "http://localhost/#p"  # no leading slash after #
    router._on_hash_change(MockEvent())
    assert router.path == "/p"

def test_router_not_found_with_path_param():
    """Cover L178: custom 404 component that accepts a 'path' keyword argument."""
    class My404WithPath(Tag.div):
        def init(self, path: str = "") -> None:
            self.text = f"Lost at: {path}"

    router = Router()
    router.add_route("/", Page)
    router.set_not_found(My404WithPath)

    router._navigate_to("/nonexistent")
    assert isinstance(router.childs[0], My404WithPath)
    assert "Lost at: /nonexistent" in router.childs[0].text
