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
