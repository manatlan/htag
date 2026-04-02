from htag.core import State, _StateProxy
from htag.tag import Tag
import pytest

def test_iteration_yields_proxies():
    """Verify that iterating over a State wrapping a list yields proxies."""
    s = State([{"id": 1}, {"id": 2}])
    
    # Track reactivity
    t = Tag.div(lambda: f"IDs: {[item['id'] for item in s]}")
    str(t)
    t._GTag__dirty = False
    
    # Iterate and mutate
    for item in s:
        assert isinstance(item, _StateProxy)
        item["id"] += 10
        
    assert t._GTag__dirty is True
    assert "IDs: [11, 12]" in str(t)

def test_states_iteration():
    """Verify that iterating over a collection in States works similarly."""
    from htag.core import States
    s = States(items=[{"v": 1}])
    
    for item in s.items:
        assert isinstance(item, _StateProxy)
        item["v"] = 42
        
    assert s.items[0]["v"] == 42
    assert s.dump()["items"][0]["v"] == 42

if __name__ == "__main__":
    pytest.main([__file__])
