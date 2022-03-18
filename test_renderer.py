#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from dataclasses import replace
import pytest
import asyncio
import re

from htag import Tag
from htag.render import Stater,HRenderer


anon=lambda t: str(t).replace( str(id(t)),"<id>" )


def getGeneratorId(resp):
    return int(re.findall( r"(\d+)", resp["next"])[0])

def test_ko_try_render_a_tagbase():
    t=Tag.div("hello")

    with pytest.raises(Exception):
        HRenderer(t,"function interact() {}; start(); // the starter")


def test_render_a_tag_with_interaction():

    class MyDiv(Tag):
        js="SCRIPT1"

        def __init__(self,**a):
            Tag.__init__(self,**a)
            self["class"]="my"

        def action(self):
            self["class"]="my2"
            self("SCRIPT2")

    t=MyDiv()
    assert t.tag == "div" # the default one
    assert t["id"] == id(t) # a inherited one got an id
    assert t["class"] == "my"
    assert str(t).startswith("<div id") # solo rendering as a div

    js=lambda t: "\n".join(t._getAllJs())

    assert "SCRIPT1" in js(t) # the script is declared in inner object
    assert str(id(t)) in js(t) # and referenced to this tag
    assert "SCRIPT2" not in js(t)

    r=HRenderer(t,"function interact() {}; start(); // the starter")
    assert t.tag == "body" # tag is now a body tag (coz main tag of renderer)

    assert ">Loading...<" in str(r) # first rendering is the loader

    # START
    resp = asyncio.run( r.interact( 0, None, None, None) )
    assert resp["update"][0]["id"] == 0
    assert "SCRIPT1" in resp["post"]
    assert "SCRIPT2" not in resp["post"]    # action not executed ... S2 not present
    assert t["class"] == "my"

    # # 1st interaction
    resp = asyncio.run( r.interact( id(t), "action", [], {}) )
    assert resp["update"][0]["id"] == id(t)
    assert "SCRIPT1" in resp["post"]    #\_ The 2 scripts are here
    assert "SCRIPT2" in resp["post"]    #/
    assert t["class"] == "my2"  # the class has changed



def test_render_a_tag_with_child_interactions():
    class Obj(Tag):
        statics=Tag.script("my")

        def __init__(self,name,**a):
            Tag.__init__(self,**a)
            self.name = name
            self.js = "INIT%s"%self.name

        def action(self):
            self("ACTION%s"%self.name)


    class MyDiv(Tag):
        statics=Tag.script("my")
        js="SCRIPT1"

        def __init__(self,**a):
            Tag.__init__(self,**a)
            self.a=Obj("A")
            self.b=Obj("B")
            self <= self.a  # NEEDED
            self <= self.b  # NEEDED

        async def action(self):
            self("SCRIPT2")
            self.a.action()
            self.b.action()

    t=MyDiv()
    r=HRenderer(t,"function interact() {}; start(); // the starter")
    assert str(r).count("<script>my</script>") == 1 # it's the same static, ensure just one !

    # START
    resp = asyncio.run( r.interact( 0, None, None, None) )
    assert resp["update"][0]["id"] == 0
    assert "SCRIPT1" in resp["post"]
    assert "INITA" in resp["post"]
    assert "INITB" in resp["post"]

    resp = asyncio.run( r.interact( id(t), "action", (), {}) )
    assert "update" not in resp
    assert "SCRIPT1" not in resp["post"]    # embbed script is not served
    assert "INITA" not in resp["post"]      # embbed script is not served
    assert "INITB" not  in resp["post"]     # embbed script is not served
    assert "ACTIONA" in resp["post"]
    assert "ACTIONB" in resp["post"]


def test_render_yield_with_scripts():
    class MyDiv(Tag):
        js="SCRIPT0"

        def init(self):
            pass

        def action(self):
            self("SCRIPT1")
            yield
            self("SCRIPT2")
            yield
            self("SCRIPT3")

        async def as_action(self):
            self("SCRIPT1")
            yield
            self("SCRIPT2")
            yield
            self("SCRIPT3")

    t=MyDiv()
    r=HRenderer(t,"function interact() {}; start(); // the starter", lambda: "ok")

    assert t.exit() == "ok", "tag.exit() doesn't work !?"

    async def testGenerator(method):
        resp = await r.interact( 0, None, None, None)
        assert resp["update"][0]["id"] == 0
        assert "SCRIPT0" in resp["post"]
        assert "next" not in resp

        resp = await r.interact( id(t), method, [],{})
        assert "update" not in resp         # NO RENDERING
        assert "SCRIPT0" not in resp["post"] # embbed script is not served
        assert "SCRIPT1" in resp["post"]


        resp = await r.interact( getGeneratorId(resp), method, None,None)    # none,none important !!!
        assert "update" not in resp         # NO RENDERING
        assert "SCRIPT0" not in resp["post"] # embbed script is not served
        assert "SCRIPT1" not in resp["post"]
        assert "SCRIPT2" in resp["post"]

        resp = await r.interact( getGeneratorId(resp), method, None,None)    # none,none important !!!
        assert "next" not in resp

        assert "update" not in resp         # NO RENDERING
        assert "SCRIPT0" not in resp["post"]
        assert "SCRIPT1" not in resp["post"]
        assert "SCRIPT2" not in resp["post"]
        assert "SCRIPT3" in resp["post"]

    asyncio.run( testGenerator("action") )
    asyncio.run( testGenerator("as_action") )


def test_interact_error():
    class MyDiv(Tag):
        def action(self):
            return 12/0

        async def as_action(self):
            return 12/0

    t=MyDiv()
    r=HRenderer(t,"function interact() {}; start(); // the starter", lambda: "ok")

    assert t.exit() == "ok", "tag.exit() doesn't work !?"

    async def testGenerator(method):
        resp = await r.interact( 0, None, None, None)
        assert resp["update"][0]["id"] == 0

        resp = await r.interact( id(t), method, [],{})
        assert "err" in resp

    asyncio.run( testGenerator("action") )
    asyncio.run( testGenerator("as_action") )

def test_intelligent_rendering():

    class Obj(Tag):

        def __init__(self,name,**a):
            Tag.__init__(self,**a)
            self["name"]=name
            self["nb"] = 0

        def inc(self):
            self["nb"] += 1

    class MyDiv(Tag):
        js="SCRIPT1"

        def __init__(self,**a):
            Tag.__init__(self,**a)
            self["nb"]=0
            self.a=Obj("A")
            self <= self.a  # NEEDED

            self.b=Obj("B")
            self <= self.b  # NEEDED

        def incMe(self):
            self["nb"] += 1

        def incA(self):
            self.a.inc()

        def incB(self):
            self.b.inc()


    t=MyDiv()

    s=Stater(t)
    assert s.guess() == []

    s=Stater(t)
    t.incA()
    assert s.guess() == [t.a]

    s=Stater(t)
    t.incB()
    assert s.guess() == [t.b]

    s=Stater(t)
    t.incMe()
    assert s.guess() == [t]

    s=Stater(t)
    t.incA()
    t.incB()
    assert s.guess() == [t.a, t.b]

    s=Stater(t)
    t.incMe()
    t.incA()
    t.incB()
    assert s.guess() == [t]


def test_intelligent_rendering2():

    class Obj(Tag):

        def __init__(self,**a):
            super().__init__(**a)
            self.nb = 0

        def inc(self):
            self.nb += 1

        def __str__(self):
            self.clear()
            self <= self.nb
            return Tag.__str__(self)

    # test that the base feature works ;-)
    o=Obj()
    assert anon(o)=='<div id="<id>">0</div>'
    o.inc()
    assert anon(o)=='<div id="<id>">1</div>'

    # test that the state image mechanism works as expected
    s_before=o._getStateImage()
    o.inc()
    s_after=o._getStateImage()
    assert s_after == s_before.replace("['1']","['2']")

    # test the stater
    o=Obj()
    s=Stater(o)
    assert s.guess() == []

    s=Stater(o)
    o.inc()
    assert s.guess() == [o]


def test_build_immediatly_vs_lately():
    """ test same behaviour """

    class Obj(Tag.div):
        """ build immediatly """

        def __init__(self,name,**a):
            Tag.__init__(self,**a)
            self["name"]=name
            self["nb"] = 0

        def inc(self):
            self["nb"] += 1
            self.clear()
            for i in range(self["nb"]):
                self <= Tag.span("*")

    class Obj2(Tag.div):
        """ build lately """

        def __init__(self,name,**a):
            Tag.__init__(self,**a)
            self.name=name
            self.nb=0

        def inc(self):
            self.nb+=1

        def __str__(self):
            self["name"]=self.name
            self["nb"]=self.nb
            self.clear()
            for i in range(self.nb):
                self <= Tag.span("*")
            return Tag.__str__(self)


    o1=Obj("toto")
    o2=Obj2("toto")

    assert anon(o1) == anon(o2)

    o1.inc()
    o2.inc()

    assert anon(o1) == anon(o2)

    o1["name"]="tata"
    o2.name = "tata"

    assert anon(o1) == anon(o2)

    o1.inc()
    o2.inc()

    assert anon(o1) == anon(o2)


def test_renderer_same_str():
    class Nimp(Tag):
        def __init__(self,name,**a):
            Tag.__init__(self,**a)
            self["name"] = name
            self <= Tag.div(name)

    o1=Nimp("hello1",_class="kiki")
    o2=Nimp(name="hello2")

    h1=HRenderer(o1,"//js")
    h2=HRenderer(o2,"//js")

    assert str(h1) == str(h2)

# test_ko_try_render_a_tagbase()
# test_render_a_tag_with_interaction()
# test_render_a_tag_with_child_interactions()
# test_render_yield_with_scripts()
# test_intelligent_rendering()
# test_build_immediatly_vs_lately()
# test_renderer_same_str()

# test_intelligent_rendering2()