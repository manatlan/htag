from htag.core import State, _StateProxy
from htag.tag import Tag
import pytest

def test_state_idempotence_basic():
    """Verify that State(my_state) is my_state."""
    s = State(42)
    s2 = State(s)
    s3 = State(s2)
    
    assert s2 is s
    assert s3 is s
    assert s.value == 42

def test_state_idempotence_proxy():
    """Verify that State(my_proxy) is my_proxy."""
    s = State({"a": 1})
    proxy = s["a"]
    # Wait, in htag v2, s["a"] for a dict returns a _StateProxy if it's a dict/list
    # But here s["a"] is '1' (int).
    
    s = State({"nested": {"val": 42}})
    proxy = s["nested"]
    assert isinstance(proxy, _StateProxy)
    
    s2 = State(proxy)
    assert s2 is proxy
    assert s2.get()["val"] == 42

def test_state_creation_normal():
    """Verify normal creation still works."""
    s = State(100)
    assert isinstance(s, State)
    assert s.value == 100

def test_state_reactivity_promotion():
    """Verify that ensuring a state maintains reactivity."""
    def sub_component(val):
        # The new recommended pattern:
        v = State(val)
        return Tag.div(lambda: f"Value: {v}")

    parent_s = State(10)
    t_shared = sub_component(parent_s)
    t_static = sub_component(20)

    # Initial render
    assert "Value: 10" in str(t_shared)
    assert "Value: 20" in str(t_static)

    # Update parent
    parent_s.value = 11
    assert "Value: 11" in str(t_shared)
    assert "Value: 20" in str(t_static)

def test_state_idempotence_observers_preserved():
    """Verify that State(s) doesn't clear observers of s."""
    s = State(0)
    t = Tag.div(lambda: s.value)
    str(t) # triggers evaluation and registration
    assert t in s._observers
    
    # "Re-promote"
    s2 = State(s)
    assert s2 is s
    assert t in s._observers # Observer should still be there!

def test_state_subclass_idempotence():
    """Verify idempotence works with State subclasses."""
    class MyState(State): pass
    
    ms = MyState(42)
    s = State(ms)
    
    assert s is ms
    assert isinstance(s, MyState)

def test_state_idempotence_recursive_proxy():
    """Verify that State(proxy) is idempotent even for deeply nested proxies."""
    s = State({"a": {"b": {"c": 42}}})
    proxy_c = s["a"]["b"]
    assert isinstance(proxy_c, _StateProxy)
    
    s_promoted = State(proxy_c)
    assert s_promoted is proxy_c
    assert s_promoted["c"] == 42
