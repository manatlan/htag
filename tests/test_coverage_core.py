import pytest
from htag import Tag, State
from htag.core import GTag

def test_state_delattr():
    class Dummy:
        pass
    d = Dummy()
    d.x = 42
    s = State(d)
    assert s.x == 42
    del s.x
    with pytest.raises(AttributeError):
        _ = d.x

def test_state_proxy_repr_str():
    s = State({"a": [1, 2]})
    proxy = s["a"]
    assert repr(proxy) == "[1, 2]"
    assert str(proxy) == "[1, 2]"

def test_state_proxy_setattr_delattr():
    class Dummy:
        pass
    d = Dummy()
    s = State({"a": d})
    proxy = s["a"]
    proxy.x = 42
    assert d.x == 42
    del proxy.x
    with pytest.raises(AttributeError):
        _ = d.x

def test_custom_id_rendering():
    t = Tag.div("hello")
    # Manually mismatch them to trigger line 397
    t.id = "internal-id"
    t["id"] = "html-id"
    html = str(t)
    assert 'id="html-id"' in html
    assert 'data-htag-id="internal-id"' in html

def test_mount_unmount_rendered_callables():
    # Covers core.py lines 522-523, 540-541
    log = []
    class Comp(Tag.div):
        def on_mount(self): log.append("mount")
        def on_unmount(self): log.append("unmount")
    
    app = Tag.App(lambda: Comp("hello"))
    # MUST render first to populate __rendered_callables
    _ = str(app) 
    
    app._trigger_mount()
    assert "mount" in log
    
    app._trigger_unmount()
    assert "unmount" in log

def test_gtag_utils():
    # Covers more of core.py
    t = Tag.div()
    t["oncustom"] = print 
    assert "custom" in t._get_events()
    del t["oncustom"]
    assert "custom" not in t._get_events()
    
    t["class"] = "a b"
    t.add_class("c")
    assert t.has_class("c")
    t.remove_class("a")
    assert not t.has_class("a")
    t.toggle_class("b") # remove b
    assert not t.has_class("b")
    t.toggle_class("d") # add d
    assert t.has_class("d")
    
    with pytest.raises(KeyError):
        del t["non-existent"]

def test_state_proxy_methods():
    # Covers core.py 207-216
    # We need a StateProxy that has a callable. A list's "append" is one.
    # But to get a StateProxy via dot notation, the State value must have the attribute.
    # Namespace simulates an object with attributes.
    class Namespace: pass
    ns = Namespace()
    ns.a = [1, 2]
    
    s = State(ns)
    proxy = s.a  # This is a _StateProxy wrapping the list
    res = proxy.append(3) # Calls _StateProxy.__getattr__ -> wrapper
    assert s.a == [1, 2, 3]
    assert res is None

def test_gtag_set_attr_direct():
    # Covers core.py 740-743
    t = Tag.div()
    t._set_attr_direct("id", "newid")
    assert t["id"] == "newid"

def test_gtag_eval_child_list():
    # Covers core.py 764-766, 775-777
    t = Tag.div(lambda: [Tag.span("a"), Tag.span("b")])
    html = str(t)
    assert ">a</span>" in html
    assert ">b</span>" in html
