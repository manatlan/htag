import pytest
from htag import State

class MockTag:
    def __init__(self):
        self._GTag__dirty = False
        self.root = None

def test_state_proxy_iadd():
    s = State(1)
    t = MockTag()
    s._observers.add(t)
    
    s += 2
    assert s.value == 3
    assert t._GTag__dirty

def test_state_proxy_method_list():
    s = State([1, 2])
    t = MockTag()
    s._observers.add(t)
    
    s.append(3)
    assert s.value == [1, 2, 3]
    assert t._GTag__dirty

def test_state_proxy_method_dict():
    s = State({"a": 1})
    t = MockTag()
    s._observers.add(t)
    
    s.update({"b": 2})
    assert s.value == {"a": 1, "b": 2}
    assert t._GTag__dirty

def test_state_proxy_getitem():
    s = State([10, 20])
    assert s[0] == 10
    assert s[1] == 20

def test_state_proxy_setitem():
    s = State({"a": 1})
    t = MockTag()
    s._observers.add(t)
    
    s["a"] = 2
    assert s.value == {"a": 2}
    assert t._GTag__dirty

def test_state_proxy_delitem():
    s = State({"a": 1, "b": 2})
    t = MockTag()
    s._observers.add(t)
    
    del s["b"]
    assert s.value == {"a": 1}
    assert t._GTag__dirty

def test_state_proxy_len():
    s = State([1, 2, 3])
    assert len(s) == 3

def test_state_proxy_iter():
    s = State([1, 2])
    items = list(iter(s))
    assert items == [1, 2]

def test_state_proxy_contains():
    s = State([1, 2])
    assert 1 in s
    assert 3 not in s

def test_state_proxy_nested_attr_no_proxy():
    # Only direct methods of the value are proxied with notify
    # If the value has an attribute that is itself an object, 
    # Calling methods on THAT object won't trigger notify of the State
    class Sub:
        def __init__(self): self.v = 0
        def inc(self): self.v += 1
    
    class obj:
        def __init__(self): self.sub = Sub()
        
    s = State(obj())
    t = MockTag()
    s._observers.add(t)
    
    s.sub.inc()
    assert s.value.sub.v == 1
    assert not t._GTag__dirty, "Deep nesting doesn't auto-notify (documented limitation)"
