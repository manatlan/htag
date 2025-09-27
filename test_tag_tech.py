#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from unittest.util import strclass
import pytest

from htag import Tag,HTagException
from htag.tag import Elements,NotBindedCaller,Caller,BaseCaller

################################################################################################################
def test_Elements():
    x=Elements()
    assert str(x)==""
    assert repr(x).startswith("<Elements ")

    x=x+42
    x=41+x
    assert str(x)=="4142"

def test_NotBindedCaller():
    x=Tag.div()
    caller = x["onclick"]
    assert isinstance(caller, NotBindedCaller)
    caller=caller+"post"
    caller="pre"+caller
    caller=caller+"post"
    caller="pre"+caller
    assert str(caller) == "pre;pre;post;post"

def test_event():
    x=Tag.div()
    assert x.event == {}


def test_caller_callable():
    def mymethod(o):
        o.called=True
    #--------------------------------------
    x=Tag.div(_onclick=mymethod)
    assert isinstance( x["onclick"],Caller )

    assert not hasattr(x,"called")
    x["onclick"]()
    assert x.called == True
    #--------------------------------------
    x=Tag.div()
    x["onclick"]=mymethod
    assert isinstance( x["onclick"],Caller )

    assert not hasattr(x,"called")
    x["onclick"]()
    assert x.called == True
    #--------------------------------------
    x=Tag.div()
    x["onclick"]=x.bind(mymethod)
    assert isinstance( x["onclick"],Caller )

    assert not hasattr(x,"called")
    x["onclick"]()
    assert x.called == True
    #--------------------------------------
    x=Tag.div()
    x["onclick"]=x.bind(mymethod, b"this.innerHTML")+"alert(42)"
    assert isinstance( x["onclick"],Caller )

    assert not hasattr(x,"called")
    x["onclick"]()
    assert x.called == True

def test_NotBindedCaller_not_callable():
    x=Tag.div()
    assert isinstance(x["onclick"], NotBindedCaller)

    with pytest.raises(TypeError):
        x["onclick"]()

    x=Tag.div(_onclick=None)
    with pytest.raises(TypeError):
        x["onclick"]()

    x=Tag.div(_onclick="")
    with pytest.raises(TypeError):
        x["onclick"]()

def test_BaseCaller_not_callable():
    x=Tag.div()
    x["onclick"] = x.bind.clear()   # create a basecaller with on a real inner method (to avoid to create a class for that ;-))
    assert isinstance(x["onclick"], BaseCaller)
    with pytest.raises(TypeError):
        x["onclick"]()


def test_Elements_radd_jules():
    x=Elements()
    x=x+42
    x=41+x
    x=[1,2]+x
    assert str(x)=="124142"

def test_NotBindedCaller_exceptions_jules():
    x=Tag.div()
    caller = x["onclick"]
    with pytest.raises(HTagException):
        caller + 42
    with pytest.raises(HTagException):
        42 + caller

def test_Caller_exceptions_jules():
    def f(): pass
    x=Tag.div()
    with pytest.raises(HTagException):
        Caller(x,"not callable",(),{})

    c=Caller(x,f,(),{})
    with pytest.raises(HTagException):
        c.bind("not callable")
    with pytest.raises(HTagException):
        c.bind(f, b"bytes not allowed")
    with pytest.raises(HTagException):
        c.bind(f, p=b"bytes not allowed")
    with pytest.raises(HTagException):
        str(c)

def test_Binder_exceptions_jules():
    x=Tag.div()
    with pytest.raises(HTagException):
        x.bind.unknownmethod()

def test_InternalCall_exceptions_jules():
    x=Tag.div()
    with pytest.raises(HTagException):
        x.call.clear()
    with pytest.raises(HTagException):
        x.call.unknownmethod()

def test_placeholder_exceptions_jules():
    x=Tag()
    assert x.tag is None
    with pytest.raises(HTagException):
        x.bind
    with pytest.raises(HTagException):
        x.call
    with pytest.raises(HTagException):
        x.attrs
    with pytest.raises(HTagException):
        x['id']
    with pytest.raises(HTagException):
        x['id'] = "x"

def test_tag_properties_jules():
    x=Tag.div()
    assert x.parent is None
    assert x.root is x

def test_tag_init_exceptions_jules():
    with pytest.raises(HTagException):
        Tag.div( render="as string" ) # render is a reserved keyword

def test_update_on_detached_tag_jules():
    import asyncio
    async def main():
        x=Tag.div()
        assert await x.update() == False
    asyncio.run(main())

def test_remove_non_child_jules():
    x=Tag.div()
    y=Tag.div()
    assert x.remove(y) is None

def test_exit_method_jules():
    class My(Tag):
        def exit(self):
            self.v=42
    x=My()
    x.exit()
    assert x.v==42


def test_add_strict_mode_jules():
    x=Tag.div()
    y=Tag.div()
    z=Tag.div()
    x.add(y)
    z.STRICT_MODE=True # set on z, not on x.root
    with pytest.raises(HTagException):
        z.add(y)

def test_setitem_multiple_callbacks_jules():
    def f1(o): o.v=1
    def f2(o): o.v=2

    x=Tag.div()
    x['onclick'] = [f1,f2]
    caller = x['onclick']
    assert caller.callback == f1
    assert len(caller._others) == 1
    assert caller._others[0][0] == f2


    x=Tag.div()
    x['onclick'] = [None,f1,None,f2,None]
    caller = x['onclick']
    assert caller.callback == f1
    assert len(caller._others) == 1
    assert caller._others[0][0] == f2


def test_repr_placeholder_jules():
    x=Tag()
    assert "PLACEHOLDER" in repr(x)

def test_str_strict_mode_render_change_jules():
    class My(Tag):
        tag="div"
        def __init__(self):
            super().__init__()
            self.cpt=0
        def render(self):
            self.cpt+=1
            self.clear( Tag.div(self.cpt) )

    x=My()
    x.root.STRICT_MODE=True
    with pytest.raises(HTagException):
        str(x)


if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
    test_Elements()
    test_NotBindedCaller()
    test_event()
    test_caller_callable()
    test_NotBindedCaller_not_callable()
    test_BaseCaller_not_callable()
    test_Elements_radd_jules()
    test_NotBindedCaller_exceptions_jules()
    test_Caller_exceptions_jules()
    test_Binder_exceptions_jules()
    test_InternalCall_exceptions_jules()
    test_placeholder_exceptions_jules()
    test_tag_properties_jules()
    test_tag_init_exceptions_jules()
    test_update_on_detached_tag_jules()
    test_remove_non_child_jules()
    test_exit_method_jules()
    test_add_strict_mode_jules()
    test_setitem_multiple_callbacks_jules()
    test_repr_placeholder_jules()
    test_str_strict_mode_render_change_jules()
