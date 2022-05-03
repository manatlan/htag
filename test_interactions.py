import pytest
import re

from htag import Tag,HTagException
from htag.render import HRenderer
import asyncio


#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#
import logging
logger = logging.getLogger(__name__)

class Simu:
    """ just to add helper method for simplify interaction / unittest

        * await init() -> dict
            for first interaction
        * await interact( Tag ).method(*args,**kargs)
            for interact on object Tag by calling method
    """


    def __init__(self,tagClass:type):
        self.hr = HRenderer(tagClass,"//")
        self.tag = self.hr.tag

    async def init(self):
        logger.debug("first interaction/init phase")
        r = await self.hr.interact( 0,None,None,None )
        assert len(r["update"])==1  # only one render (the main)
        assert r["update"][0]       # first is 0 ;-)
        return r

    def interact(self,o: Tag = None):
        assert isinstance(o,Tag)

        class Binder:
            def __getattr__(this,name:str):
                async def _(*a,**k):
                    logger.debug("interaction with %s, call %s(*%s,**%s)",repr(o),name,a,k)
                    return await self.hr.interact( id(o),name,a,k)
                return _

        return Binder()

    async def doNext(self,r):
        assert "next" in r
        assert r["next"].count(": null") == 3
        id=int(re.findall( r"(\d+)", r["next"])[0])

        return await self.hr.interact( id,None,None,None)

#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#=#


class Object(Tag):
    def init(self):
        self["nb"]=0

    def incNormal(self):
        self["nb"]+=1

    def incNoRedraw(self):
        self["nb"]+=1


@pytest.mark.asyncio
async def test_simplest():  #TODO: redefine coz norender is gone, so this test is perhaps non sense
    hr=Simu( Object )
    o = hr.tag
    r=await hr.init()

    r=await hr.interact(o).incNormal()
    assert list(r["update"].keys()) == [ id(o) ]

    # r=await hr.interact(o).incNoRedraw()
    # assert r=={}

@pytest.mark.asyncio
async def test_rendering(): #TODO: redefine coz norender is gone, so this test is perhaps non sense

    class P(Tag):
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

    r=await hr.init()

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

    class Object(Tag):
        def init(self):
            self["nb"]=0

        def inc(self):
            self["nb"]+=1
            yield

    hr=Simu(Object)
    o=hr.tag

    r=await hr.init()

    r=await hr.interact(o).inc()
    assert "update" in r

    await hr.doNext( r)
    assert "update" in r


@pytest.mark.asyncio
async def test_yield():

    class Object(Tag):

        def inc(self):
            yield
            yield list("abc")
            yield "d"


    hr=Simu(Object)
    o=hr.tag

    r=await hr.init()

    assert o.childs==[]

    r=await hr.interact(o).inc()

    # first yield, yield nothing
    assert o.childs==[]

    assert r["next"]
    assert "stream" not in r

    r=await hr.doNext( r)

    # seconf yield, yield list("abc")
    assert o.childs==['a', 'b', 'c']
    assert "stream" in r
    assert r["stream"][id(o)]=="abc"
    assert r["next"]
    assert ">abc<" in str(o)

    r=await hr.doNext( r)

    assert o.childs==['a', 'b', 'c', 'd']
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



if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    # asyncio.run( test1() )
    # asyncio.run( test2() )
    # asyncio.run( test_simplest_async() )
    # asyncio.run( test_yield() )
    asyncio.run( test_rendering() )
    # asyncio.run( test_bug() )
