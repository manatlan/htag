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

def test_instantiation_no_warning(capsys):
    """
    Ensures that underscore-prefixed attributes during instantiation
    do NOT trigger a deprecation warning anymore AND correctly map to HTML attributes.
    """
    t = Tag.div(_class="myclass", _onclick="alert(1)")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert t["class"] == "myclass"
    assert t["onclick"] == "alert(1)"


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
