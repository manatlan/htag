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

        assert self.tag.parent is None          # ensure no parent !
        assert self.tag._hr == self.hr          # the tag has received its "_hr" !
        assert self.tag.tag == "body"           # tag converted to body

        self._1stInteraction = False

    async def init(self):
        """ do the 1st interaction, and control that it update '0' only ! """
        logger.debug("first interaction/init phase")
        r = await self.hr.interact( 0,None,None,None )
        assert len(r["update"])==1              # only one render (the main)
        assert r["update"][0]                   # first is 0 ;-)
        assert r["update"][0]==str(self.tag)    # it's the str(hr.tag) !
        self._1stInteraction = True
        return r

    def interact(self,o: Tag = None):
        assert self._1stInteraction, "First interaction not done !"
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
    await s.init() # it controls the basics

@pytest.mark.asyncio
async def test_js_at_init1():
    class Object(Tag.div):
        def init(self):
            self("interaction_js();")
    ########################################################
    s=Simu( Object )
    r=await s.init() # it controls the basics
    assert "interaction_js();" in r["post"]
    assert r["post"].count("function(tag)")==1

@pytest.mark.asyncio
async def test_js_at_init2():
    class Object(Tag.div):
        js = "static_js();"
    ########################################################
    s=Simu( Object )
    r=await s.init() # it controls the basics
    assert "static_js();" in r["post"]
    assert r["post"].count("function(tag)")==1

@pytest.mark.asyncio
async def test_js_at_init3():
    class Object(Tag.div):
        js = "static_js();"
        def init(self):
            self("interaction_js();")
    ########################################################
    s=Simu( Object )
    r=await s.init() # it controls the basics
    assert "interaction_js();" in r["post"]
    assert "static_js();" in r["post"]
    assert r["post"].count("function(tag)")==2

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

    await s.init() # it controls the basics
    assert s.tag["nb"]==0

    r=await s.interact().changeContent()
    assert s.tag["nb"]==1
    assert list(r["update"].keys()) == [ id(s.tag) ]
    assert r["update"][id(s.tag)]==str(s.tag)
    assert ' nb="1"></body>' in r["update"][id(s.tag)]

    r=await s.interact().doNothing()
    assert "update" not in r

    r=await s.interact().addContent()
    assert len(s.tag.childs)==1
    assert list(r["update"].keys()) == [ id(s.tag) ]
    assert r["update"][id(s.tag)]==str(s.tag)
    assert ' nb="1">content</body>' in r["update"][id(s.tag)]


    r=await s.interact().all()
    assert s.tag["nb"]==2
    assert len(s.tag.childs)==2
    assert list(r["update"].keys()) == [ id(s.tag) ]
    assert r["update"][id(s.tag)]==str(s.tag)
    assert ' nb="2">contentcontent</body>' in r["update"][id(s.tag)]

if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)

    asyncio.run( test_empty() )
    asyncio.run( test_js_at_init1() )
    asyncio.run( test_js_at_init2() )
    asyncio.run( test_js_at_init3() )
    asyncio.run( test_simplest() )
