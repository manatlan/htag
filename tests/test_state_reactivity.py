import pytest
from htag import State, Tag

def test_state_iadd_reactivity():
    s = State(["A"])
    dirty = False
    
    class MockTag:
        def __init__(self):
            self._GTag__dirty = False
    
    t = MockTag()
    s._observers.add(t)
    
    # In-place addition
    s.value += ["B"]
    
    assert t._GTag__dirty, "Tag should be marked dirty after += on State.value"

def test_state_set_reactivity():
    s = State(["A"])
    class MockTag:
        def __init__(self):
            self._GTag__dirty = False
    
    t = MockTag()
    s._observers.add(t)
    
    s.set(s.value + ["B"])
    
    assert t._GTag__dirty, "Tag should be marked dirty after .set() on State"

def test_state_assignment_reactivity():
    s = State(0)
    class MockTag:
        def __init__(self):
            self._GTag__dirty = False
    
    t = MockTag()
    s._observers.add(t)
    
    s.value = 1
    
    assert t._GTag__dirty, "Tag should be marked dirty after value assignment"
