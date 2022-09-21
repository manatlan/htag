from htag import Tag,HTagException
from htag.render import HRenderer
import asyncio

import htbulma as b
import pytest

def test_base():
    # test a placeholder
    B=Tag.B()

    s= Tag()    # placeholder !
    s += B

    # properties not available for placeholder
    with pytest.raises(HTagException):
        s["koko"]="kk"
    with pytest.raises(HTagException):
        v=s["koko"]

    with pytest.raises(HTagException):
        s.attrs["kkk"]=42

    with pytest.raises(HTagException):
        print(s.attrs)

    with pytest.raises(HTagException):
        print(s.bind)

    assert s.tag is None
    assert str(s) == "<B></B>"
    assert s.innerHTML == "<B></B>"
    assert s.childs[0] == B

    assert s._getTree() == { s: [ {B:[]} ]}

    assert "placeholder" in repr(s).lower()


def test_at_construction():
    with pytest.raises(HTagException):
        Tag(_onclick="kkk")    # can't autoset html attrs at construction time

    # but, can autoset instance properties at construction time
    t=Tag(value=42)
    assert t.value==42

    t=Tag(js=42)    #TODO: SHOULD'NT BE POSSIBLE TOO !
    assert t.js==42


    t=Tag( Tag.A()+Tag.B() )
    assert str(t) == "<A></A><B></B>"



@pytest.mark.asyncio
async def test_placeholder_to_body():
    """ many js statements rendered """

    class App(Tag):
        imports=[]  # to avoid importing all scopes
        def init(self):
            self += "hello"

    #TODO: use Simu ;-)
    hr=HRenderer( App, "// my starter")

    # the placeholder is converted to a real body !
    # to be interact'able, and have a consistence as a "main tag"
    assert hr.tag.tag == "body"

    # first interaction
    r=await hr.interact(0,None,None,None,None)

    assert r["update"][0] == f'<body id="{id(hr.tag)}">hello</body>'

import re
def anon(x):
    return re.sub(r'id="\d+"','*id*',str(x))

@pytest.mark.asyncio
async def test_using_a_placeholder():
    """ many js statements rendered """

    class Jo(Tag):
        def init(self):
            self <= Tag.b("hello")+Tag.c("world")

        def cls(self):
            self.clear()

    class App(Tag.body):
        imports=[]  # to avoid importing all scopes
        def init(self):
            self += Jo()

    #TODO: use Simu ;-)
    hr=HRenderer( App, "// my starter")

    # first interaction
    r=await hr.interact(0,None,None,None,None)
    print(r)
    assert anon(r["update"][0] ) == "<body *id*><b *id*>hello</b><c *id*>world</c></body>"

    ## interact with jo instance (call cls)
    jo = hr.tag.childs[0]
    r=await hr.interact( id(jo), "cls", [], {})
    print(r["update"])
    assert id(jo) not in r["update"]


if __name__=="__main__":
    test_base()
    test_at_construction()
    asyncio.run( test_placeholder_to_body() )
    asyncio.run( test_using_a_placeholder() )