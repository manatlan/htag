
from htag.core import State, GTag, App
from htag.tag import Tag
import pytest

def test_automatic_dereferencing_in_eval_child():
    """Verify that _eval_child returns the value, even for non-callables (Feature #2)."""
    s = State(False)
    t = Tag.div()
    
    # Before, this might have returned the State object if stringify=False
    val = t._eval_child(s, stringify=False)
    assert val is False
    assert isinstance(val, bool)
    
    # And it should register t as an observer!
    assert t in s._observers

def test_attribute_reactivity_direct_state():
    """Verify that attributes passed as State objects are reactive (Feature #3)."""
    class MockApp(App):
        def __init__(self):
            super().__init__()
            self.update_called = 0
        def update(self):
            self.update_called += 1
            
    s = State(False)
    t = Tag.button("Click", _disabled=s)
    app = MockApp()
    app.add(t)
    
    # Force first render of the whole tree (which calls _render_attrs on t)
    _ = str(app) 
    
    # At this point, t should be observing s
    assert t in s._observers
    
    # Mutating s should trigger app.update()
    s.value = True
    assert app.update_called == 1

def test_state_truthiness_in_logic():
    """Verify the case mentioned in ToFix #2: logic using _eval_child."""
    s = State(False)
    t = Tag.div()
    
    # In a component's logic:
    loading = s
    val = t._eval_child(loading, stringify=False)
    if val:
        pytest.fail(f"Should be False! (was {val})")
    
    s.value = True
    if not t._eval_child(loading, stringify=False):
        pytest.fail("Should be True!")

def test_nested_state_dereferencing():
    """Verify that _eval_child handles nested State/Proxies."""
    inner = State(True)
    s = State({"active": inner})
    t = Tag.div()
    
    val = t._eval_child(s["active"], stringify=False)
    assert val is True
    assert t in inner._observers # inner was accessed
