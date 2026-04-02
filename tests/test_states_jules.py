import pytest
from htag.core import States, State

def test_states_init_jules():
    s = States(a=1, b="hello")
    assert isinstance(s.a, State)
    assert s.a.get() == 1
    assert isinstance(s.b, State)
    assert s.b.get() == "hello"

def test_states_getattr_jules():
    s = States(val=42)
    assert s.val == 42 # Uses State's __eq__
    assert s.val.get() == 42

    with pytest.raises(AttributeError):
        _ = s.missing

def test_states_setattr_jules():
    s = States(val=10)
    s.val = 20
    assert s.val.get() == 20

    # Check that in-place operators work through the proxy
    s.val += 5
    assert s.val.get() == 25

    with pytest.raises(AttributeError, match="Cannot create attribute"):
        s.new_val = 100

def test_states_dump_jules():
    s = States(x=1, y=2, z=[1, 2])
    s.z.append(3)
    data = s.dump()
    assert data == {"x": 1, "y": 2, "z": [1, 2, 3]}

def test_states_load_jules():
    s = States(x=1, y=2)
    s.load({"x": 10, "new_var": "created"})

    assert s.x.get() == 10
    assert s.y.get() == 2
    assert s.new_var.get() == "created"
    assert s.dump() == {"x": 10, "y": 2, "new_var": "created"}
