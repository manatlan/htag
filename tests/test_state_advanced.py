from htag.core import State, _ctx
from htag.tag import Tag
import pytest

def test_iterative_reactivity():
    """Test that iterating over a State yields proxies that can trigger updates."""
    s = State([{"n": 1}, {"n": 2}])
    t = Tag.div(lambda: "".join(str(item["n"]) for item in s))
    
    # Initial render
    assert str(t).endswith(">12</div>")
    t._GTag__dirty = False
    
    # Iterate and mutate nested item
    for item in s:
        if item["n"] == 1:
            item["n"] = 42 # Modifying the item through the iterator!
            
    assert t._GTag__dirty is True
    assert str(t).endswith(">422</div>")

def test_set_reactivity():
    """Test that set operations are reactive."""
    s = State({1, 2})
    t = Tag.div(lambda: str(len(s)))
    
    # Render
    str(t)
    t._GTag__dirty = False
    
    s.add(3)
    assert t._GTag__dirty is True
    assert str(t).endswith(">3</div>")
    
    t._GTag__dirty = False
    s.remove(1)
    assert t._GTag__dirty is True
    assert str(t).endswith(">2</div>")

def test_tuple_nesting_reactivity():
    """Test that reactivity works through tuples (which are immutable but can contain proxies)."""
    s = State( ([1], [2]) )
    t = Tag.div(lambda: str(s[0][0]))
    
    # Render
    str(t)
    t._GTag__dirty = False
    
    # Access list through tuple, and append
    s[0].append(99)
    assert t._GTag__dirty is True

def test_attribute_delegation():
    """Test that setting attributes directly on the State delegates to the value."""
    class User:
        def __init__(self, name): self.name = name
        
    u = User("Alice")
    s = State(u)
    t = Tag.div(lambda: s.name)
    
    # Render
    assert str(t).endswith(">Alice</div>")
    t._GTag__dirty = False
    
    # DIRECT attribute assignment on the State object
    s.name = "Bob"
    
    assert u.name == "Bob"
    assert t._GTag__dirty is True
    assert str(t).endswith(">Bob</div>")

def test_attribute_deletion_delegation():
    """Test that deleting attributes on the State delegates to the value."""
    class Obj: pass
    o = Obj()
    o.temp = 42
    s = State(o)
    
    del s.temp
    assert not hasattr(o, "temp")
