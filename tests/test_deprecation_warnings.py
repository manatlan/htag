import pytest
import logging
from htag import Tag

def test_instantiation_no_warning(capsys):
    """
    Ensures that underscore-prefixed attributes during instantiation
    do NOT trigger a deprecation warning.
    """
    t = Tag.div(_class="myclass", _onclick="alert(1)")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert t["class"] == "myclass"
    assert t["onclick"] == "alert(1)"

def test_getattr_warning(capsys):
    """
    Ensures that accessing underscore-prefixed attributes triggers a warning.
    """
    t = Tag.div(_class="myclass")
    _ = capsys.readouterr() # clear
    c = t._class
    assert c == "myclass"
    captured = capsys.readouterr()
    assert "DEPRECATION" in captured.out
    assert "Accessing HTML attributes via underscore prefix ('_class')" in captured.out

def test_setattr_warning(capsys):
    """
    Ensures that setting underscore-prefixed attributes triggers a warning.
    """
    t = Tag.div()
    _ = capsys.readouterr() # clear
    t._class = "newclass"
    assert t["class"] == "newclass"
    captured = capsys.readouterr()
    assert "DEPRECATION" in captured.out
    assert "Setting HTML attributes via underscore prefix ('_class')" in captured.out

def test_get_event_warning(capsys):
    """
    Ensures that accessing underscore-prefixed events triggers a warning.
    """
    t = Tag.div(_onclick="alert(1)")
    _ = capsys.readouterr() # clear
    oc = t._onclick
    assert oc == "alert(1)"
    captured = capsys.readouterr()
    assert "DEPRECATION" in captured.out
    assert "Accessing events via underscore prefix ('_onclick')" in captured.out

def test_set_event_warning(capsys):
    """
    Ensures that setting underscore-prefixed events triggers a warning.
    """
    t = Tag.div()
    _ = capsys.readouterr() # clear
    t._onclick = "alert(2)"
    assert t["onclick"] == "alert(2)"
    captured = capsys.readouterr()
    assert "DEPRECATION" in captured.out
    assert "Setting events via underscore prefix ('_onclick')" in captured.out

def test_getattr_no_warning_on_missing(capsys):
    """
    Accessing a non-existent underscore attribute should still raise AttributeError or return what super does,
    but shouldn't warn if it doesn't exist in attrs/events.
    """
    t = Tag.div()
    _ = capsys.readouterr() # clear
    with pytest.raises(AttributeError):
        _ = t._non_existent
    captured = capsys.readouterr()
    assert captured.out == ""
