from htag.core import State, GTag, _ctx
from htag.tag import Tag
import pytest

def test_state_get_basic():
    """Test State.get() with various types."""
    s_bool = State(True)
    assert s_bool.get() is True
    
    s_int = State(42)
    assert s_int.get() == 42
    
    s_dict = State({"a": 1})
    assert s_dict.get() == {"a": 1}
    
    s_list = State([1, 2, 3])
    assert s_list.get() == [1, 2, 3]

def test_proxy_get_basic():
    """Test _StateProxy.get() with nested structures."""
    s = State({"nested": {"val": 42}, "items": [1, 2, 3]})
    
    # Proxy to dict
    proxy_dict = s["nested"]
    assert proxy_dict.get() == {"val": 42}
    
    # Proxy to list
    proxy_list = s["items"]
    assert proxy_list.get() == [1, 2, 3]

def test_state_get_reactivity():
    """Test that State.get() registers observers for reactivity."""
    s = State("initial")
    t = Tag.div(lambda: f"Value: {s.get()}")
    
    # Initial render should register observer
    assert str(t).endswith(">Value: initial</div>")
    assert t in s._observers
    t._GTag__dirty = False
    
    # Modification should trigger re-render
    s.value = "updated"
    assert t._GTag__dirty is True
    assert str(t).endswith(">Value: updated</div>")

def test_proxy_get_reactivity():
    """Test that _StateProxy.get() registers observers for reactivity."""
    s = State({"nested": {"val": "initial"}})
    proxy = s["nested"] # This is a _StateProxy
    t = Tag.div(lambda: f"Value: {proxy.get()['val']}")
    
    # Initial render should register observer
    assert str(t).endswith(">Value: initial</div>")
    assert t in s._observers
    t._GTag__dirty = False
    
    # Modification should trigger re-render
    s["nested"]["val"] = "updated"
    assert t._GTag__dirty is True
    assert str(t).endswith(">Value: updated</div>")

def test_state_get_no_side_effects():
    """Ensure get() does not trigger notification (it's a read operation)."""
    s = State("val")
    t = Tag.div(lambda: s.get())
    str(t)
    t._GTag__dirty = False
    
    # Calling get() again should NOT mark observer as dirty
    s.get()
    assert t._GTag__dirty is False
