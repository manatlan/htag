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
