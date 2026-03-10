import pytest
import logging
from htag import Tag

def test_instantiation_no_warning(caplog):
    """
    Ensures that underscore-prefixed attributes during instantiation
    do NOT trigger a deprecation warning.
    """
    with caplog.at_level(logging.WARNING, logger="htag"):
        t = Tag.div(_class="myclass", _onclick="alert(1)")
        assert len(caplog.records) == 0
        assert t["class"] == "myclass"
        assert t["onclick"] == "alert(1)"

def test_getattr_warning(caplog):
    """
    Ensures that accessing underscore-prefixed attributes triggers a warning.
    """
    t = Tag.div(_class="myclass")
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="htag"):
        c = t._class
        assert c == "myclass"
        assert len(caplog.records) == 1
        assert "DEPRECATION" in caplog.text
        assert "Accessing HTML attributes via underscore prefix ('_class')" in caplog.text

def test_setattr_warning(caplog):
    """
    Ensures that setting underscore-prefixed attributes triggers a warning.
    """
    t = Tag.div()
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="htag"):
        t._class = "newclass"
        assert t["class"] == "newclass"
        assert len(caplog.records) == 1
        assert "DEPRECATION" in caplog.text
        assert "Setting HTML attributes via underscore prefix ('_class')" in caplog.text

def test_get_event_warning(caplog):
    """
    Ensures that accessing underscore-prefixed events triggers a warning.
    """
    t = Tag.div(_onclick="alert(1)")
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="htag"):
        oc = t._onclick
        assert oc == "alert(1)"
        assert len(caplog.records) == 1
        assert "DEPRECATION" in caplog.text
        assert "Accessing events via underscore prefix ('_onclick')" in caplog.text

def test_set_event_warning(caplog):
    """
    Ensures that setting underscore-prefixed events triggers a warning.
    """
    t = Tag.div()
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="htag"):
        t._onclick = "alert(2)"
        assert t["onclick"] == "alert(2)"
        assert len(caplog.records) == 1
        assert "DEPRECATION" in caplog.text
        assert "Setting events via underscore prefix ('_onclick')" in caplog.text

def test_getattr_no_warning_on_missing(caplog):
    """
    Accessing a non-existent underscore attribute should still raise AttributeError or return what super does,
    but shouldn't warn if it doesn't exist in attrs/events.
    """
    t = Tag.div()
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger="htag"):
        with pytest.raises(AttributeError):
            _ = t._non_existent
        assert len(caplog.records) == 0
