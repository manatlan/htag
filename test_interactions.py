import pytest
import re

"""
Theses are End-2-End tests

"""


from htag import Tag,HTagException
from htag.render import HRenderer
import asyncio

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
import logging
logger = logging.getLogger(__name__)


class Simu:
    """ just a class helper for simplify interaction / unittest
        * await init() -> dict
            for first interaction
        * await interact( Tag|None ).method(*args,**kargs) -> dict
            for interact on object Tag by calling method
        * await doNext -> dict
            to continue generator interactions
    """

    def __init__(self,tagClass:type):
        self.hr = HRenderer(tagClass,"//")
        self.tag = self.hr.tag

        assert self.tag.parent is None          # ensure no parent !
        assert self.tag._hr == self.hr          # the tag has received its "_hr" !
        assert self.tag.tag == "body"           # tag converted to body

        # self._1stInteraction = False

    # async def init(self):
    #     """ do the 1st interaction, and control that it update '0' only ! """
    #     logger.debug("first interaction/init phase")
    #     r = await self.hr.interact( 0,None,None,None )
    #     assert len(r["update"])==1              # only one render (the main)
    #     assert r["update"][0]                   # first is 0 ;-)
    #     assert r["update"][0]==str(self.tag)    # it's the str(hr.tag) !
    #     self._1stInteraction = True
    #     return r

    def interact(self,o: Tag = None):
        # assert self._1stInteraction, "First interaction not done !"
        if o is None: o = self.tag
        assert isinstance(o,Tag)

        class Binder:
            def __getattr__(this,name:str):
                async def _(*a,**k):
                    logger.debug("interaction with %s, call %s(*%s,**%s)",repr(o),name,a,k)
                    return await self.hr.interact( id(o),name,a,k)
                return _

        return Binder()

    async def doNext(self,r):
        # ensure next statement is here
        assert "next" in r

        # ensure all params are null
        assert r["next"].count(": null") == 3

        # except the first (id)
        id=int(re.findall( r"(\d+)", r["next"])[0])

        return await self.hr.interact( id,None,None,None)

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#


@pytest.mark.asyncio
async def test_empty():
    class Object(Tag.div):
        pass
    ########################################################
    s=Simu( Object )
    # await s.init() # it controls the basics

@pytest.mark.asyncio
async def test_js_at_init1():
    class Object(Tag.div):
        def init(self):
            self.call("interaction_js();")
    ########################################################
    s=Simu( Object )
    # r=await s.init() # it controls the basics
    assert "interaction_js();" in str(s.hr)
    # assert r["post"].count("function(tag)")==1

@pytest.mark.asyncio
async def test_js_at_init_new_InternalCall():
    class Object(Tag.div):
        def init(self):
            self.call.mymethod("hello") # same as self.call( self.bind.mymethod('hello') )
        def mymethod(self,msg):
            assert msg=="hello"
    ########################################################
    s=Simu( Object )
    # r=await s.init() # it controls the basics

    assert "function(self){ try{interact(" in str(s.hr)
    # assert r["post"].count("function(tag)")==1



@pytest.mark.asyncio
async def test_js_at_init2():
    class Object(Tag.div):
        js = "static_js();"
    ########################################################
    s=Simu( Object )
    # r=await s.init() # it controls the basics
    assert "static_js();" in str(s.hr)

    # assert r["post"].count("function(tag)")==1

@pytest.mark.asyncio
async def test_js_at_init3():
    class Object(Tag.div):
        js = "static_js();"
        def init(self):
            self.call("interaction_js();")
    ########################################################
    s=Simu( Object )
    # r=await s.init() # it controls the basics
    assert "interaction_js();" in str(s.hr)
    assert "static_js();" in str(s.hr)
    # assert r["post"].count("function(tag)")==2

@pytest.mark.asyncio
async def test_simplest():
    class Object(Tag.div):
        def init(self):
            self["nb"]=0

        def changeContent(self):
            self["nb"]+=1

        def doNothing(self):
            self.done = "nothing"

        def addContent(self):
            self <= "content"

        def all(self):
            self.changeContent()
            self.addContent()

    ########################################################
    s=Simu( Object )

    # await s.init() # it controls the basics
    assert s.tag["nb"]==0

    r=await s.interact().changeContent()
    assert s.tag["nb"]==1
    assert list(r["update"].keys()) == [ id(s.tag) ]
    assert r["update"][id(s.tag)]==str(s.tag)
    assert ' nb="1" ' in r["update"][id(s.tag)]

    r=await s.interact().doNothing()
    assert "update" not in r

    r=await s.interact().addContent()
    assert len(s.tag.childs)==1
    assert list(r["update"].keys()) == [ id(s.tag) ]
    assert r["update"][id(s.tag)]==str(s.tag)
    assert ' nb="1" ' in r["update"][id(s.tag)]


    r=await s.interact().all()
    assert s.tag["nb"]==2
    assert len(s.tag.childs)==2
    assert list(r["update"].keys()) == [ id(s.tag) ]
    assert r["update"][id(s.tag)]==str(s.tag)
    assert ' nb="2" ' in r["update"][id(s.tag)]
    assert 'contentcontent' in r["update"][id(s.tag)]


@pytest.mark.asyncio
async def test_rendering(): #TODO: redefine coz norender is gone, so this test is perhaps non sense

    class Object(Tag.div):
        def init(self):
            self["nb"]=0

        def incNormal(self):
            self["nb"]+=1

        def incNoRedraw(self):
            self["nb"]+=1


    class P(Tag.div):
        def init(self):

            self.o1 = Object()
            self <= self.o1

            self["my"]=0

        def testModO1_1(self):
            self.o1.incNormal()

        def testModO1_2(self):
            self.o1.incNoRedraw()


        # use incNormal from o1

        def testModMe_0(self):
            self["my"]+=1

        def testModMe_1(self):
            self["my"]+=1
            self.o1.incNormal()     # has no efect

        # @Tag.NoRender
        # def testModMe_2(self):
        #     self["my"]+=1
        #     self.o1.incNormal()     # has no efect


        # use incNoRedraw from o1

        def testModMe_10(self):
            self["my"]+=1

        def testModMe_11(self):
            self["my"]+=1
            self.o1.incNoRedraw()   # has no efect

        # @Tag.NoRender
        # def testModMe_12(self):
        #     self["my"]+=1
        #     self.o1.incNoRedraw()   # has no efect

    #====================================================================

    hr=Simu( P )
    o=hr.tag

    # r=await hr.init()

    # will interact on "o1", by calling main (o's) methods
    r=await hr.interact( o ).testModO1_1()
    assert id(o.o1) in r["update"]  # just o1 has changed

    # r=await hr.interact( o ).testModO1_2()
    # assert id(o.o1) in r["update"]  # just o1 has changed

    #========================

    r=await hr.interact( o ).testModMe_0()
    assert id(o) in r["update"]

    r=await hr.interact( o ).testModMe_1()
    assert id(o) in r["update"] # in fact, redraw main

    # r=await hr.interact( o ).testModMe_2()
    # assert id(o.o1) in r["update"]  # redraw just the child # not the main, coz main return 0

    # #========================

    r=await hr.interact( o ).testModMe_10()
    assert id(o) in r["update"]

    r=await hr.interact( o ).testModMe_11()
    assert id(o) in r["update"] # in fact, redraw main

    # r=await hr.interact( o ).testModMe_12()
    # assert id(o.o1) in r["update"]  # redraw just the child # not the main, coz main return 0




@pytest.mark.asyncio
async def test_simplest_async(): #TODO: redefine coz norender is gone, so this test is perhaps non sense

    class Object(Tag.div):
        def init(self):
            self["nb"]=0

        def inc(self):
            self["nb"]+=1
            yield

    hr=Simu(Object)
    o=hr.tag

    # r=await hr.init()

    r=await hr.interact(o).inc()
    assert "update" in r

    await hr.doNext( r)
    assert "update" in r


@pytest.mark.asyncio
async def test_yield():

    class Object(Tag.div):

        def inc(self):
            yield
            yield list("abc")
            yield "d"


    hr=Simu(Object)
    o=hr.tag

    # r=await hr.init()

    assert o.childs==()

    r=await hr.interact(o).inc()

    # first yield, yield nothing
    assert o.childs==()

    assert r["next"]
    assert "stream" not in r

    r=await hr.doNext( r)

    # seconf yield, yield list("abc")
    assert o.childs==('a', 'b', 'c')
    assert "stream" in r
    assert r["stream"][id(o)]=="abc"
    assert r["next"]
    assert ">abc<" in str(o)

    r=await hr.doNext( r)

    assert o.childs==('a', 'b', 'c', 'd')
    assert "stream" in r
    assert r["stream"][id(o)]=="d"
    assert r["next"]
    assert ">abcd<" in str(o)

    r=await hr.doNext( r)
    assert r=={}

@pytest.mark.asyncio
async def test_bug():
    S=Simu( Tag.div )
    r=await S.hr.interact(15654654654546,"m",(),{})
    assert r["err"] # 15654654654546 is not an existing Tag or generator (dead objects ?)?!"

@pytest.mark.asyncio
async def test_bug_0_8_5():
    """ many js statements rendered """

    class Comp(Tag.div):
        def init(self):
            self.js = "console.log('YOLO');"

    class App(Tag.body):
        def init(self):
            self += Tag.div( Tag.div( Comp() ) )

    #TODO: use Simu ;-)
    hr=HRenderer( App, "// my starter")

    assert len(App()._getAllJs()) == 1

    # # first interaction
    # r=await hr.interact(hr.tag,None,None,None,None)

    # # I should just find 1 YOLO (1 js) ... (but in 0.8.5 -> 4 ;-( )
    assert str(hr).count("YOLO") == 1
    # print(r)




if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    # asyncio.run( test_empty() )
    # asyncio.run( test_js_at_init1() )
    # asyncio.run( test_js_at_init2() )
    # asyncio.run( test_js_at_init3() )
    # asyncio.run( test_simplest() )
    # asyncio.run( test_bug_0_8_5() )
    asyncio.run( test_js_at_init_new_InternalCall() )
