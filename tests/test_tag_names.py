# -*- coding: utf-8 -*-
from htag import Tag
from htag.core import GTag

def test_tag_creator_hyphenation():
    # Tag.sl_button should result in tag name "sl-button"
    b = Tag.sl_button("hello")
    assert b.tag == "sl-button"
    assert str(b).startswith("<sl-button")

def test_tag_creator_multiple_underscores():
    # Tag.my_custom_web_component should result in "my-custom-web-component"
    t = Tag.my_custom_web_component()
    assert t.tag == "my-custom-web-component"
    assert str(t).startswith("<my-custom-web-component")

def test_gtag_direct_hyphenation():
    # Tag.some_tag() should result in "some-tag"
    t = Tag.some_tag()
    assert t.tag == "some-tag"
    assert str(t).startswith("<some-tag")

def test_no_underscore_still_works():
    # Tag.div should still be "div"
    d = Tag.div()
    assert d.tag == "div"
    
    # Tag.span() should still be "span"
    s = Tag.span()
    assert s.tag == "span"


def test_forbidden_tag_names():
    import pytest
    for name in ["add", "remove", "clear", "update", "call", "bind"]:
        with pytest.raises(AttributeError):
            getattr(Tag, name)
        with pytest.raises(AttributeError):
            getattr(Tag, name.upper())

