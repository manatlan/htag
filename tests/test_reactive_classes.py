
from htag.core import State, GTag
from htag.tag import Tag
import pytest

def test_add_class_on_lambda():
    """Verify that add_class works on a lambda class (Fix #4)."""
    t = Tag.div()
    t["class"] = lambda: "initial"
    
    # Should wrap the lambda and not crash
    t.add_class("added")
    
    # Check current attribute is a callable
    assert callable(t["class"])
    
    # Evaluate it
    res = t._eval_child(t["class"], stringify=False)
    assert res == "initial added"

def test_remove_class_on_lambda():
    """Verify that remove_class works on a lambda class (Fix #4)."""
    t = Tag.div()
    t["class"] = lambda: "foo bar"
    t.remove_class("foo")
    
    res = t._eval_child(t["class"], stringify=False)
    assert res == "bar"

def test_toggle_class_on_lambda():
    """Verify that toggle_class works on a lambda class (Fix #4)."""
    t = Tag.div()
    t["class"] = lambda: "a b"
    t.toggle_class("a")
    t.toggle_class("c")
    
    res = t._eval_child(t["class"], stringify=False)
    assert res == "b c"

def test_scoped_styles_with_lambda_class():
    """Verify that scoped styles (styles="...") work with lambda classes (Fix #4)."""
    class Scoped(Tag.div):
        styles = ".test { color: red; }"
        def init(self):
            # Attempting to use a lambda for class in a scoped component
            self["class"] = lambda: "my-class"
            
    # When instantiated:
    # 1. GTag.__init__ sets self["class"] to lambda
    # 2. GTag.__init__ calls self.add_class(scope_cls)
    # THIS is where it used to crash.
    t = Scoped()
    
    res = t._eval_child(t["class"], stringify=False)
    assert "my-class" in res
    assert f"htag-{Scoped.__name__}" in res

def test_add_class_on_state():
    """Verify that add_class updates a State object directly."""
    s = State("btn")
    t = Tag.div(_class=s)
    
    t.add_class("btn-lg")
    
    assert s.value == "btn btn-lg"
    assert t["class"] is s # Still the same State object
    
    # To become an observer, the State MUST be evaluated via _eval_child (usually during render)
    _ = t._render_attrs() 
    assert t in s._observers
    
    # Observation check
    t._GTag__dirty = False
    s.value = "btn changed"
    assert t._GTag__dirty is True
