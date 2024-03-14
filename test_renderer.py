#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from collections import UserDict
from dataclasses import replace
import pytest
import asyncio
import re

from htag import Tag,HTagException
from htag.render import Stater,HRenderer,fmtcaller



anon=lambda t: str(t).replace( str(id(t)),"<id>" )

def test_fmtcaller():
    fmtcaller("jo",(b"yo","yo",b'nom et prenom du gars', 'nom et prenom du gars',42,True,3.2, None), {'test': 3,"byt":b"jkjjkjkjkjjkjkjkjkjkj"})
    fmtcaller("jo",(42,),{})
    fmtcaller("jo",("court",),{})
    fmtcaller("jo",("court, mais tres long",),{})
    fmtcaller("jo",(b"court",),{})
    fmtcaller("jo",(b"court, mais tres long",),{})
    fmtcaller("jo",(),dict(a="court"))
    fmtcaller("jo",(),dict(a="court, mais tres long"))
    fmtcaller("jo",(),dict(a=42,b=None,c=True,d=3.14))
    fmtcaller("jo",(),dict(a=[1,2,3],b=dict(a=42)))

def getGeneratorId(resp):
    return int(re.findall( r"(\d+)", resp["next"])[0])

# def test_ko_try_render_a_tagbase():

#     with pytest.raises(HTagException):
#         HRenderer(H.div,"function interact() {}; start(); // the starter")

def test_ok_including_a_Tag_in_statics():
    class Style(Tag):
        tag="mystyle"

    class O(Tag):
        statics= [Style()]  # <= avoid that (does nothing!!!)

    r=HRenderer(O,"function interact() {}; start(); // the starter")
    assert "<mystyle>" in str(r) # will not be included
    # and a logger.warning is outputed

def test_statics_in_real_statics():
    # s1=Tag.H.div( [1,"h",Tag.div("dyn"),Tag.H.div("dyn",_id=12)] )
    s2=Tag.div( [1,"h",Tag.div("stat"),Tag.Section( Tag.div("yolo") )] )

    # assert "id=" in str(s1)
    # assert str(s1._ensureTagBase()) =='<div>1h<div>dyn</div><div id="12">dyn</div></div>'
    # assert "id=" in str(s2)
    assert str(s2) =="<div>1h<div>stat</div><Section><div>yolo</div></Section></div>"

def test_render_title():

    class MyDiv(Tag.div):
        pass

    r=HRenderer(MyDiv,"function interact() {}; start(); // the starter")
    assert str(r).find("<title>MyDiv</title>") > 0

    class MyDiv(Tag.div):
        statics = Tag.title("hello")

    r=HRenderer(MyDiv,"function interact() {}; start(); // the starter")
    p1= str(r).find("<title>hello</title>")
    p2 = str(r).find("<title>MyDiv</title>")
    assert p1 < p2

def test_render_a_tag_with_interaction():

    class MyDiv(Tag.div):
        js="SCRIPT1"

        def __init__(self,**a):
            Tag.__init__(self,**a)
            self["class"]="my"

        def action(self):
            self["class"]="my2"
            self.call("SCRIPT2")

    t=MyDiv()
    assert t.tag == "div" # the default one
    assert t["id"] == None
    assert t["class"] == "my"
    assert str(t).startswith("<div class") # solo rendering as a div

    js=lambda t: "\n".join(t._getAllJs())

    assert "SCRIPT1" in js(t) # the script is declared in inner object
    assert str(id(t)) in js(t) # and referenced to this tag
    assert "SCRIPT2" not in js(t)

    r=HRenderer(MyDiv,"function interact() {}; start(); // the starter")
    t=r.tag
    assert t.tag == "body" # tag is now a body tag (coz main tag of renderer)

    # assert ">Loading...<" in str(r) # first rendering is the loader

    # # START
    # resp = asyncio.run( r.interact( 0, None, None, None) )
    # assert 0 in resp["update"]
    # assert "SCRIPT1" in resp["post"]
    # assert "SCRIPT2" not in resp["post"]    # action not executed ... S2 not present
    # assert t["class"] == "my"

    # # 1st interaction
    resp = asyncio.run( r.interact( id(t), "action", [], {}) )
    assert id(t) in resp["update"]
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
            self.call("ACTION%s"%self.name)


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
            self.call("SCRIPT2")
            self.a.action()
            self.b.action()

    r=HRenderer(MyDiv,"function interact() {}; start(); // the starter")
    t=r.tag
    assert str(r).count("<script>my</script>") == 1 # it's the same static, ensure just one !

    # # START
    # resp = asyncio.run( r.interact( 0, None, None, None) )
    # assert 0 in resp["update"]
    # assert "SCRIPT1" in resp["post"]
    # assert "INITA" in resp["post"]
    # assert "INITB" in resp["post"]

    resp = asyncio.run( r.interact( id(t), "action", (), {}) )
    assert "update" not in resp
    print("=====",resp)
    # assert "SCRIPT1" not in resp["post"]    # embbed script is not served
    # assert "INITA" not in resp["post"]      # embbed script is not served
    # assert "INITB" not  in resp["post"]     # embbed script is not served
    # assert "ACTIONA" in resp["post"]
    # assert "ACTIONB" in resp["post"]


def test_render_yield_with_scripts():
    class MyDiv(Tag):
        js="SCRIPT0"

        def init(self):
            pass

        def action(self):
            self.call("SCRIPT1")
            yield
            self.call("SCRIPT2")
            yield
            self.call("SCRIPT3")

        async def as_action(self):
            self.call("SCRIPT1")
            yield
            self.call("SCRIPT2")
            yield
            self.call("SCRIPT3")

    r=HRenderer(MyDiv,"function interact() {}; start(); // the starter", lambda: "ok")
    t=r.tag

    assert t.exit() == "ok", "tag.exit() doesn't work !?"

    async def testGenerator(method):
        # resp = await r.interact( 0, None, None, None)
        # assert 0 in resp["update"]
        assert "SCRIPT0" in str(r)
        # assert "SCRIPT0" in resp["post"]
        # assert "next" not in resp

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

    r=HRenderer(MyDiv,"function interact() {}; start(); // the starter", lambda: "ok")
    t=r.tag

    assert t.exit() == "ok", "tag.exit() doesn't work !?"

    async def testGenerator(method):
        # resp = await r.interact( 0, None, None, None)
        # assert 0 in resp["update"]

        resp = await r.interact( id(t), method, [],{})
        assert "err" in resp

    asyncio.run( testGenerator("action") )
    asyncio.run( testGenerator("as_action") )

def test_intelligent_rendering():

    class Obj(Tag.div):

        def __init__(self,name,**a):
            Tag.__init__(self,**a)
            self["name"]=name
            self["nb"] = 0

        def inc(self):
            self["nb"] += 1

    class MyDiv(Tag.div):
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

    class Obj(Tag.div):

        def __init__(self,**a):
            super().__init__(**a)
            self.nb = 0

        def inc(self):
            self.nb += 1

        def render(self):
            self.clear()
            self <= self.nb

    # test that the base feature works ;-)
    o=Obj()
    assert str(o)=='<div>0</div>'
    o.inc()
    assert str(o)=='<div>1</div>'

    # test that the state image mechanism works as expected
    s_before=o._getStateImage()
    o.inc()
    s_after=o._getStateImage()
    ######################################################
    ######################################################
    ######################################################
    # assert s_after == s_before.replace(">1<",">2<") with _getStateImage() -> pure str
    ######################################################
    ######################################################
    ######################################################
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
            Tag.div.__init__(self,**a)
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

        def render(self):
            self.clear()
            self["name"]=self.name
            self["nb"]=self.nb
            for i in range(self.nb):
                self <= Tag.span("*")


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


# def test_renderer_same_str():
#     class Nimp(Tag):
#         def __init__(self,name,**a):
#             Tag.__init__(self,**a)
#             self["name"] = name
#             self <= Tag.div(name)

#     o1=Nimp("hello1",_class="kiki")
#     o2=Nimp(name="hello2")

#     h1=HRenderer(o1,"//js")
#     h2=HRenderer(o2,"//js")

#     assert str(h1) == str(h2)


def test_discovering_js():
    class O(Tag.div):
        js="/*JS1*/"

    # dynamic js init is present (THE BIGGEST CHANGE since the beginning of no_0_interaction)
    assert "/*JS1*/" in str(HRenderer( O, "//"))

    class OOI(Tag.div): # immediate rendering
        def init(self):
            self.clear( O() )             # Tag directly in Tag

    class OOOI(Tag.div):  # immediate rendering
        def init(self):
            self.clear( Tag.div( O() ) )  # Tag in a TagBase

    class OOL(Tag.div):   # lately rendering
        def render(self):
            self.clear()
            self.clear( O() )             # Tag directly in Tag

    class OOOL(Tag.div):  # lately rendering
        def render(self): # BAD PRACTICE (creating a tag in render will always force rendering) !!!!!!!!!!!!!!!!!!
            self.clear()
            self.clear( Tag.div(O()) )    # Tag in a TagBase

    async def test(r): # first call (init obj)
        # resp = await r.interact( r.tag, None, None, None)
        # assert 0 in resp["update"]
        # assert "/*JS1*/" in resp["post"]
        print("===",r)
        assert "/*JS1*/" in str(r)

    r=HRenderer(OOI,"//js interact")
    asyncio.run(test(r))

    r=HRenderer(OOOI,"//js interact")
    asyncio.run(test(r))

    # r=HRenderer(OOL,"//js interact")
    # asyncio.run(test(r))

    # r=HRenderer(OOOL,"//js interact")
    # asyncio.run(test(r))


# this test is NON SENSE, til statics are imported in static (not dynamic anymore)
# this test is NON SENSE, til statics are imported in static (not dynamic anymore)
# this test is NON SENSE, til statics are imported in static (not dynamic anymore)
def test_discovering_css():
    class O(Tag):
        statics=[Tag.style("/*CSS1*/")]

    class OOI(Tag.div): # immediate rendering
        def init(self):
            self.clear( O() )             # Tag directly in Tag

    class OOOI(Tag.div):  # immediate rendering
        def init(self):
            self.clear( Tag.div( O() ) )  # Tag in a TagBase

    class OOL(Tag.div):   # lately rendering
        def render(self):
            self.clear( O() )             # Tag directly in Tag

    class OOOL(Tag.div):  # lately rendering
        def render(self):
            self.clear( Tag.div(O()) )    # Tag in a TagBase

    def test(r): # first call (init obj)
        assert "/*CSS1*/" in str(r)


    r=HRenderer(OOI,"//js interact")
    test(r)

    r=HRenderer(OOOI,"//js interact")
    test(r)

    r=HRenderer(OOL,"//js interact")
    test(r)

    r=HRenderer(OOOL,"//js interact")
    test(r)

def test_imports():

    class Ya(Tag.div):
        statics = Tag.style("""body {font-size:100px}""", _id="Ya")

        def init(self):
            self <= "Ya"


    class Yo(Tag.div):
        statics = Tag.style("""body {background:#CFC;}""", _id="Yo")

        def init(self):
            self <= "Yo"


    class AppWithImport(Tag.body):
        statics = Tag.style("""body {color: #080}""", _id="main")
        imports = Yo

        def init(self):
            self <= Yo()

    class AppWithoutImport(Tag.body):
        statics = Tag.style("""body {color: #080}""", _id="main")

        def init(self):
            self <= Yo()

    html=str(HRenderer( AppWithImport, ""))
    styles = re.findall("(<style[^<]+</style>)",html)
    assert len(styles)==2

    html=str(HRenderer( AppWithoutImport, ""))
    styles = re.findall("(<style[^<]+</style>)",html)
    assert len(styles)>2


    class AppWithBrokenImport(Tag.body):
        imports = "nimpnawak"               # not a Tag class !? -> error

        def init(self):
            self <= Yo()

    # this works ...
    str(AppWithBrokenImport())

    # this not !
    with pytest.raises(HTagException):
        HRenderer(AppWithBrokenImport,"//js")


def test_new():
    class APP(Tag.div):
        def init(self,val=42):
            self <= f"=={val}=="

    # syntax of versions < 0.4 is not supported anymore
    with pytest.raises(TypeError):
        HRenderer( APP(),"//" )

    # new syntax
    hr=HRenderer( APP,"//" )
    assert str(hr).startswith("<!DOCTYPE html>")

    async def assertion(txt):
        # actions = await hr.interact( 0, None, None, None)
        assert txt in str(hr)

    # ensure first interaction produce the right thing
    asyncio.run( assertion(">==42==</body>") )


    #-----------------
    # new syntax (with init first arg) : OK
    hr=HRenderer( APP,"//", init=((43,),{}) )
    assert str(hr).startswith("<!DOCTYPE html>")

    # async def assertion(txt):
    #     # actions = await hr.interact( 0, None, None, None)
    #     # assert txt in actions["update"][0]
    #     assert txt in str(hr)

    # ensure first interaction produce the right thing
    asyncio.run( assertion(">==43==</body>") )


    #-----------------
    # new syntax (with init as keyword arg) : ok
    hr=HRenderer( APP,"//", init=((),dict(val=44)) )
    assert str(hr).startswith("<!DOCTYPE html>")

    # async def assertion(txt):
    #     # actions = await hr.interact( 0, None, None, None)
    #     # assert txt in actions["update"][0]
    #     assert txt in str(hr)


    # ensure first interaction produce the right thing
    asyncio.run( assertion(">==44==</body>") )


    #-----------------
    # new syntax (with init first arg) : KO (coz too many args)
    hr=HRenderer( APP,"//", init=((45,49),{}) )
    assert str(hr).startswith("<!DOCTYPE html>")

    # async def assertion(txt):
    #     # actions = await hr.interact( 0, None, None, None)
    #     # assert txt in actions["update"][0]
    #     assert txt in str(hr)

    # ensure first interaction produce the right thing
    asyncio.run( assertion(">==42==</body>") )


    #-----------------
    # new syntax (with init as bad keyword arg) : KO (bad args)
    hr=HRenderer( APP,"//", init=((),dict(myval=50)) )
    assert str(hr).startswith("<!DOCTYPE html>")

    # async def assertion(txt):
    #     # actions = await hr.interact( 0, None, None, None)
    #     # assert txt in actions["update"][0]
    #     assert txt in str(hr)

    # ensure first interaction produce the right thing
    asyncio.run( assertion(">==42==</body>") )


def test_new_base():
    class App(Tag.div):
        def init(self,m="default",**a):
            self <= m
            self <= Tag.span("world")

    #til it's not in a hrenderer, there is no @id
    assert str( App() ) == "<div>default<span>world</span></div>"

    # and you can add yourself, if needed
    assert str( App(_id="myid") ) == '<div id="myid">default<span>world</span></div>'

    hr=HRenderer(App,"")
    assert str(hr.tag).count("id=") == 2 # body & span



def test_just_4_coverage():
    """ will enter in the exception trapped, but will produce a body tag"""
    hr=HRenderer(Tag.div,"",init=("kk",{None:None},42))
    assert hr.tag.tag=="body"


def test_STRICT_MODE_in_render():
    try:
        Tag.STRICT_MODE = True

        #--------------------------------- a good case
        class Good(Tag.div):    # good because render() doesn't modify its direct childs
            def render(self):
                a=42

        print(Good()) # force rendering

        #--------------------------------- a bad case
        class Bad(Tag.div):
            def render(self):
                self += Tag.div("yo")

        with pytest.raises(HTagException):
            print( Bad() )

        #--------------------------------- a good case
        class Good2(Tag.div):
            def render(self):
                self += "simple text is not enough !!!"

        print( Good2() )

    finally:
        Tag.STRICT_MODE = False



def test_state_and_session():
    class LocalApp(Tag.div):
        imports=[]
        def init(self):
            self.state["hello"]=42
            self <= Tag.span("hello")

    # assert that the state works in all cases
    str( LocalApp() ) # TypeError: 'NoneType' object does not support item assignment

    ses=dict(user="moi")

    hr=HRenderer(LocalApp,"",session=ses,fullerror=True)
    assert str(hr).count("id=") == 2 # body & span

    assert hr.tag.state
    assert "hello" in hr.tag.state

    assert hr.tag.state["hello"]==42

    assert hr.tag.state.export() == dict(hello=42)

    assert len(ses)==2

    hr.tag.state.clear()
    assert not hr.tag.state

    assert len(ses)==1

    hr.tag.state.load( dict(world=43) )

    assert len(ses)==2
    assert hr.tag.state["world"]==43

    del hr.tag.state["world"]
    assert not hr.tag.state
    assert len(ses)==1

if __name__=="__main__":
    # test_ko_try_render_a_tagbase()
    # test_render_a_tag_with_interaction()
    # test_render_a_tag_with_child_interactions()
    # test_render_yield_with_scripts()
    # test_intelligent_rendering()
    # test_build_immediatly_vs_lately()
    # test_renderer_same_str()

    # test_intelligent_rendering2()

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)

    # test_intelligent_rendering()
    # test_statics_in_real_statics()
    # test_render_yield_with_scripts()
    # test_statics_in_real_statics()
    # test_render_title()
    # test_new()
    # test_render_a_tag_with_child_interactions()
    # test_render_a_tag_with_interaction()
    # test_new_base()
    # test_intelligent_rendering2()
    # test_just_4_coverage()
    # test_avoid_tagcreation_in_render()
    # test_discovering_js()
    test_state_and_session()