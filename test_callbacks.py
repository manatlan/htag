import pytest
import re

from htag import Tag,HTagException
from htag.render import HRenderer
import asyncio

from htag.tag import Caller

def test_simple_callback():
    def action():
        pass

    s=Tag.button("hello",_onclick=action)

    assert isinstance( s["onclick"], Caller )
    caller=s["onclick"]
    assert caller.instance == s
    assert caller.callback == action
    assert caller.args == ()
    assert caller.kargs == {}
    assert f"onclick-{id(s)}" == caller._assigned
    print(caller._assigned, s._callbacks_)
    assert caller._assigned in s._callbacks_
    assert s._callbacks_[ caller._assigned ] == caller

def test_simple_binded_himself_callback():
    def action():
        pass

    s=Tag.button("hello")
    s["onclick"]=s.bind( action )

    assert isinstance( s["onclick"], Caller )
    caller=s["onclick"]
    assert caller.instance == s
    assert caller.callback == action
    assert caller.args == ()
    assert caller.kargs == {}
    assert f"onclick-{id(s)}" == caller._assigned
    assert caller._assigned in s._callbacks_
    assert s._callbacks_[ caller._assigned ] == caller


def test_multiple_binded_himself_callback():
    def action1():
        pass
    def action2():
        pass

    s=Tag.button("hello")
    s["onclick"]=s.bind( action1 ).bind( action2 )

    assert isinstance( s["onclick"], Caller )
    caller=s["onclick"]
    assert caller.instance == s
    assert caller.callback == action1
    assert caller.args == ()
    assert caller.kargs == {}
    assert f"onclick-{id(s)}" == caller._assigned
    assert caller._assigned in s._callbacks_
    assert s._callbacks_[ caller._assigned ] == caller

    assert caller._others==[ (action2,(),{})]


def test_binded_parent_callback(): # args/kargs
    def action():
        pass

    p=Tag.div()
    s=Tag.button("hello",_onclick=p.bind( action, b"this.value", p=42 ) )

    assert isinstance( s["onclick"], Caller )
    caller=s["onclick"]
    assert caller.instance == p
    assert caller.callback == action
    assert caller.args == (b"this.value",)
    assert caller.kargs == dict(p=42)
    assert f"onclick-{id(s)}" == caller._assigned
    assert caller._assigned not in s._callbacks_
    assert caller._assigned in p._callbacks_
    assert p._callbacks_[ caller._assigned ] == caller

    print(p)
    print(s)
    print(caller)

if __name__=="__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
    logger = logging.getLogger("htag.tag")
    logger.setLevel(logging.INFO)

    test_simple_callback()
    test_simple_binded_himself_callback()
    test_binded_parent_callback()
    test_multiple_binded_himself_callback()

