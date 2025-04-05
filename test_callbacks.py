#!./venv/bin/python3
import pytest
import re

from htag import Tag,HTagException,expose
from htag.render import HRenderer
import asyncio
from test_interactions import Simu

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
    assert caller._assigned in s._callbacks_
    assert s._callbacks_[ caller._assigned ] == caller

    # try to rebind
    def action2():
        pass

    s["onclick"] = action2
    assert len(s._callbacks_)==1

    caller=s["onclick"]
    assert caller.instance == s
    assert caller.callback == action2
    assert caller.args == ()
    assert caller.kargs == {}
    assert f"onclick-{id(s)}" == caller._assigned
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





def test_binded_concatenate_strings(): #TODO: need more tests
    def action1(o):
        pass

    s=Tag.button("hello")

    s["onclick"]=s.bind( action1 )+"let x=42"
    assert ";let x=42;}" in str(s)

    s["onclick"]="let x=41"+s.bind( action1 )
    assert "try{let x=41;" in str(s)

    # can't add str to a callback not binded (logical!)
    with pytest.raises(TypeError):
        s["onclick"]=action1+"let x=42;"

    # cant add non-str to a Caller
    with pytest.raises(HTagException):
        s["onclick"]=s.bind(action1)+42
    with pytest.raises(HTagException):
        s["onclick"]=42+s.bind(action1)

    # and it works too for old binders (self.bind.<method>())
    class A(Tag.div):
        def init(self):
            self <= Tag.button("1",_onclick=self.bind.action()+"let x=42")
            self <= Tag.button("2",_onclick="let x=41"+self.bind.action())
        def action(self):
            pass
    s=str(A()) # TODO: not terrible
    assert ";let x=42;}" in s
    assert "try{let x=41;" in s

def test_binded_parent_callback(): # args/kargs
    def action(o):
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

def test_ko():
    x=Tag.a("link",_onclick="alert(42)")
    x["onclick"] = "alert(42)"


    rt=Tag.div()
    a=Tag.a("link")
    a["onclick"]=rt.bind( test_ko )                            # possible
    assert isinstance( a["onclick"], Caller )

    a=Tag.a("link")
    a["onclick"]=test_ko                                       # possible but non sens
    assert isinstance( a["onclick"], Caller )

    a=Tag.a("link")
    with pytest.raises(TypeError):
        a["onclick"]=a.bind()
    with pytest.raises(HTagException):
        a["onclick"]=a.bind(None)
    with pytest.raises(HTagException):
        a["onclick"]=a.bind(a.bind(None)) # not double bind
    with pytest.raises(HTagException):
        a["onclick"]=a.bind("")
    with pytest.raises(HTagException):
        a["onclick"]=a.bind(test_ko).bind("nimp")
    with pytest.raises(HTagException):
        a["onclick"]=a.bind(test_ko).bind( test_ko, b"this.value")    # not possible to bind a js in a second binder (just the first)

    with pytest.raises(TypeError):
        a["onclick"]=a.bind(test_ko).bind() # non sens


    with pytest.raises(HTagException):
        str( a.bind(test_ko) )    # not possible coz not assigned to a Tag !

    a["onclick"]=a.bind(test_ko).bind(None).bind(None) # possible



# def test_prior():
#     def action1():
#         pass
#     def action2():
#         pass

#     s=Tag.button("hello")
#     callback = s.bind( action1 )

#     #----------------------------------------
#     s["onclick"]=callback

#     assert isinstance( s["onclick"], Caller )
#     caller=s["onclick"]
#     assert caller.instance == s
#     assert caller.callback == action1   # action1 is first !
#     assert caller._others == []
#     assert caller.args == ()
#     assert caller.kargs == {}
#     assert f"onclick-{id(s)}" == caller._assigned
#     assert caller._assigned in s._callbacks_
#     assert s._callbacks_[ caller._assigned ] == caller

#     #----------------------------------------
#     s["onclick"]=callback.prior( action2 )

#     assert isinstance( s["onclick"], Caller )
#     caller=s["onclick"]
#     assert caller.instance == s
#     assert caller.callback == action2   # action2 is now first !
#     assert caller._others[0][0] == action1 # action1 is next
#     assert caller.args == ()
#     assert caller.kargs == {}
#     assert f"onclick-{id(s)}" == caller._assigned
#     assert caller._assigned in s._callbacks_
#     assert s._callbacks_[ caller._assigned ] == caller


def test_on_event():
    def action1(obj):   # classic
        assert isinstance(obj,Tag) and obj.tag=="button"
    async def action2(obj): # async method
        assert isinstance(obj,Tag) and obj.tag=="button"
    def action3(obj):   # classic generator
        assert isinstance(obj,Tag) and obj.tag=="button"
        yield "hello"
    async def action4(obj): # async generator
        assert isinstance(obj,Tag) and obj.tag=="button"
        yield "hello"


    async def test():
        evt = s["onclick"]._assigned
        return [i async for i in s.__on__( evt )]

    ############################################################
    # test btn handling simple callback
    ############################################################

    s=Tag.button("hello", _onclick = action1)
    assert asyncio.run( test() ) == []
    #----------------------------------------------------
    s=Tag.button("hello", _onclick = action2)
    assert asyncio.run( test() ) == []
    #----------------------------------------------------
    s=Tag.button("hello", _onclick = action3)
    assert asyncio.run( test() ) == [ "hello" ]
    #----------------------------------------------------
    s=Tag.button("hello", _onclick = action4)
    assert asyncio.run( test() ) == [ "hello" ]




    ############################################################
    # test btn handling binded callback
    ############################################################

    s=Tag.button("hello")
    s["onclick"]= s.bind( action1)
    assert asyncio.run( test() ) == []
    #----------------------------------------------------
    s=Tag.button("hello")
    s["onclick"]= s.bind( action2)
    assert asyncio.run( test() ) == []
    #----------------------------------------------------
    s=Tag.button("hello")
    s["onclick"]= s.bind( action3)
    assert asyncio.run( test() ) == [ "hello" ]
    #----------------------------------------------------
    s=Tag.button("hello")
    s["onclick"]= s.bind( action4)
    assert asyncio.run( test() ) == [ "hello" ]

    ############################################################
    # test btn handling theirs events
    ############################################################
    class App(Tag.div):
        def __init__(self):
            super().__init__()
            self <= Tag.button("hello", _onclick = self.action1)
            self <= Tag.button("hello", _onclick = self.action2)
            self <= Tag.button("hello", _onclick = self.action3)
            self <= Tag.button("hello", _onclick = self.action4)

        def action1(self, o):   # classic
            assert isinstance(o,Tag) and o.tag=="button"
        async def action2(self, o): # async method
            assert isinstance(o,Tag) and o.tag=="button"
        def action3(self, o):   # classic generator
            assert isinstance(o,Tag) and o.tag=="button"
            yield "hello"
        async def action4(self, o): # async generator
            assert isinstance(o,Tag) and o.tag=="button"
            yield "hello"


    async def test(nb):
        app=App()
        o=app.childs[nb]
        evt = o["onclick"]._assigned
        return [i async for i in o.__on__( evt )]   # execute on button

    assert asyncio.run( test(0) ) ==[]
    assert asyncio.run( test(1) ) ==[]
    assert asyncio.run( test(2) ) ==["hello"]
    assert asyncio.run( test(3) ) ==["hello"]


    ############################################################
    # test app handling btn events
    ############################################################

    class App(Tag.div):
        def __init__(self):
            super().__init__()
            self <= Tag.button("hello", _onclick = self.bind( self.action1 ))
            self <= Tag.button("hello", _onclick = self.bind( self.action2 ))
            self <= Tag.button("hello", _onclick = self.bind( self.action3 ))
            self <= Tag.button("hello", _onclick = self.bind( self.action4 ))

        def action1(self):   # classic
            pass
        async def action2(self): # async method
            pass
        def action3(self):   # classic generator
            yield "hello"
        async def action4(self): # async generator
            yield "hello"


    async def test(nb):
        app=App()
        o=app.childs[nb]
        evt = o["onclick"]._assigned
        return [i async for i in app.__on__( evt )]   # execute on app

    assert asyncio.run( test(0) ) ==[]
    assert asyncio.run( test(1) ) ==[]
    assert asyncio.run( test(2) ) ==["hello"]
    assert asyncio.run( test(3) ) ==["hello"]


def test_list_of_callers(): #TODO: need more tests
    def action(obj):   # classic generator
        assert isinstance(obj,Tag) and obj.tag=="button"
        yield "hello"    

    def action2(o):
        o.iwashere = "world"   

    async def test():
        evt = s["onclick"]._assigned
        return [i async for i in s.__on__( evt )]

    s=Tag.button("hello", _onclick = action)
    assert asyncio.run( test() ) == ["hello"]
    s=Tag.button("hello", _onclick = [action])  # exactly the same as ^^
    assert asyncio.run( test() ) == ["hello"]

    s=Tag.button("hello", _onclick = [None,action,None,action,action2])
    assert asyncio.run( test() ) == ["hello","hello"]
    assert s.iwashere == "world"

def test_auto_expose():
    class Jo(Tag.div):
        def init(self):
            self <= Tag.button("hello",_onclick="self.action(42)" )
        def action(self,val):
            assert val == 42

    # assert no @expose, no auto declared
    s=Simu(Jo)
    assert "self.action = function(_)" not in str(s.hr)

    class Jo(Tag.div):
        def init(self):
            self <= Tag.button("hello",_onclick="self.action(42)" )
        @expose
        def action(self,val):
            assert val == 42

    # assert with @expose, it's now autodeclared
    s=Simu(Jo)
    assert "self.action = function(_)" in str(s.hr)

    #TODO: should test that the click do what it can do

if __name__=="__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
    logger = logging.getLogger("htag.tag")
    logger.setLevel(logging.INFO)

    # test_simple_callback()
    # test_simple_binded_himself_callback()
    # test_binded_parent_callback()
    # test_multiple_binded_himself_callback()

    # test_on_event()
    # test_ko()
    # test_try_to_bind_on_tagbase()
    # test_binded_concatenate_strings()
    # test_auto_expose()
    test_list_of_callers()