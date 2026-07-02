import pytest
from htag.exceptions import HtagError, HtagRenderError, HtagEventError

def test_exceptions_inheritance():
    # Vérifie que tout hérite bien de HtagError
    with pytest.raises(HtagError):
        raise HtagRenderError("render error")
    
    with pytest.raises(HtagError):
        raise HtagEventError("event error")

def test_exception_messages():
    e1 = HtagRenderError("msg1")
    assert str(e1) == "msg1"
    
    e2 = HtagEventError("msg2")
    assert str(e2) == "msg2"


def test_lshift_unsupported():
    from htag import Tag
    t1 = Tag.div()
    t2 = Tag.span()
    with pytest.raises(TypeError) as excinfo:
        t1 << t2
    assert "L'opérateur '<<' n'est pas supporté" in str(excinfo.value)

