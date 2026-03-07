from htag.core import State, GTag, _ctx
from htag.tag import Tag
import pytest

def test_state_nested_list_reactivity():
    """Test that modifying a list inside a State triggers re-render."""
    s = State([1, 2])
    t = Tag.div(lambda: f"Len: {len(s)}")
    
    # Initial render
    assert str(t).endswith(">Len: 2</div>")
    assert t in s._observers
    t._GTag__dirty = False
    
    # Mutate nested list
    s.append(3)
    assert t._GTag__dirty is True
    assert str(t).endswith(">Len: 3</div>")

def test_state_nested_dict_reactivity():
    """Test that modifying a dict inside a State triggers re-render."""
    s = State({"a": 1})
    t = Tag.div(lambda: f"Val: {s['a']}")
    
    # Initial render
    assert str(t).endswith(">Val: 1</div>")
    t._GTag__dirty = False
    
    # Mutate nested dict
    s["a"] = 2
    assert t._GTag__dirty is True
    assert str(t).endswith(">Val: 2</div>")

def test_state_deep_nested_reactivity():
    """Test reactivity on deeply nested structures (proxy of proxy)."""
    s = State({"users": [{"name": "Alice"}]})
    t = Tag.div(lambda: f"Name: {s['users'][0]['name']}")
    
    # Initial render
    assert str(t).endswith(">Name: Alice</div>")
    t._GTag__dirty = False
    
    # Deep mutation
    s["users"][0]["name"] = "Bob"
    assert t._GTag__dirty is True
    assert str(t).endswith(">Name: Bob</div>")

def test_state_comparison_operators():
    """Test all comparison operators and their ability to register observers."""
    s = State(10)
    
    # Greater than
    t_gt = Tag.div(lambda: "Yes" if s > 5 else "No")
    assert str(t_gt).endswith(">Yes</div>")
    assert t_gt in s._observers
    
    # Equal
    t_eq = Tag.div(lambda: "Yes" if s == 10 else "No")
    assert str(t_eq).endswith(">Yes</div>")
    
    # Less than
    t_lt = Tag.div(lambda: "Yes" if s < 15 else "No")
    assert str(t_lt).endswith(">Yes</div>")
    
    t_gt._GTag__dirty = False
    s.value = 3
    assert t_gt._GTag__dirty is True

def test_state_arithmetic_operators():
    """Test arithmetic operators work and return raw values (or result of op)."""
    s = State(10)
    assert s + 5 == 15
    assert s - 2 == 8
    assert s * 2 == 20
    assert s / 2 == 5.0
    assert s // 3 == 3
    assert s % 3 == 1
    assert s ** 2 == 100

def test_state_unary_operators():
    """Test unary operators (-s, abs(s), etc.)."""
    s = State(-10)
    assert -s == 10
    assert abs(s) == 10
    assert +s == -10

def test_state_type_conversions():
    """Test explicit and implicit type conversions."""
    # Boolean
    s_bool = State(0)
    assert bool(s_bool) is False
    s_bool.value = 1
    assert bool(s_bool) is True
    
    # Integer
    s_int = State("42")
    assert int(s_int) == 42
    
    # Float
    s_float = State("3.14")
    assert float(s_float) == 3.14

def test_state_call_reactivity():
    """Test that calling the state s() registers an observer."""
    s = State("hello")
    # Using the call protocol inside a lambda
    t = Tag.div(lambda: s())
    
    assert str(t).endswith(">hello</div>")
    assert t in s._observers
    t._GTag__dirty = False
    
    s.value = "world"
    assert t._GTag__dirty is True

def test_proxy_call_reactivity():
    """Test that calling a proxy s['a']() registers an observer."""
    s = State({"func": lambda: "result"})
    t = Tag.div(lambda: s["func"]())
    
    assert str(t).endswith(">result</div>")
    assert t in s._observers

def test_state_hashability():
    """Ensure State and Proxies are hashable (identity-based)."""
    s = State({"a": 1})
    p = s["a"]
    
    # Should not raise TypeError
    d = {s: "state", p: "proxy"}
    assert d[s] == "state"
    assert d[p] == "proxy"
