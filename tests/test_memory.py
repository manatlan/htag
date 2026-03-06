import gc
import weakref
import pytest
from htag.core import State
from htag import Tag

def test_state_observer_garbage_collection():
    """Verify that State doesn't keep alive components that are no longer used."""
    s = State(0)
    
    # Define a component in a local scope
    def create_and_observe():
        t = Tag.div(lambda: f"v={s.value}")
        # Initial render to register observation
        _ = str(t)
        return weakref.ref(t)

    wref = create_and_observe()
    
    # At this point, t should be in s._observers
    # But ONLY via WeakSet
    
    # Force garbage collection
    gc.collect()
    
    # The component should be dead if there are no other references
    assert wref() is None
    
    # The observers list should be empty (or at least t should be gone)
    assert len(s._observers) == 0

def test_state_notifies_living_observers():
    """Verify that multiple living components are still notified."""
    s = State(0)
    
    t1 = Tag.div(lambda: s.value)
    t2 = Tag.div(lambda: s.value)
    
    # Register observations
    str(t1)
    str(t2)
    
    assert len(s._observers) == 2
    
    t1._GTag__dirty = False
    t2._GTag__dirty = False
    
    s.value = 1
    
    assert t1._GTag__dirty is True
    assert t2._GTag__dirty is True
    
def test_state_does_not_leaks_nested_tags():
    """Verify that tags created inside reactive lambdas are also collectable."""
    s = State(0)
    
    wrefs = []
    
    def render():
        t_inner = Tag.span("inner")
        wrefs.append(weakref.ref(t_inner))
        return t_inner
        
    t_outer = Tag.div(lambda: render())
    
    # Initial render
    str(t_outer)
    
    assert wrefs[0]() is not None
    
    # Clear outer or just wait for it to be cleared
    t_outer.clear()
    gc.collect()
    
    # Inner tag should be collectible now
    assert wrefs[0]() is None
