from htag import Tag,HTagException
from htag.render import HRenderer,Stater
import asyncio
from pprint import pprint

import pytest

import re
def anon(x):
    return re.sub(r'id="\d+"','*id*',str(x))

def test_concept():
    h= Tag.hello("world")
    t=Tag(Tag(Tag(Tag( h ))))
    assert str(h) == str(t)

def test_concept_inherited():
    class PlaceHolder(Tag):
        pass

    h= Tag.hello("world")
    t=PlaceHolder(PlaceHolder(PlaceHolder(PlaceHolder( h ))))
    assert str(h) == str(t)



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


def test_tree():

    # normal case (just verify all is ok)
    t=Tag.body()

    A= Tag.A()
    B= Tag.B()
    C= Tag.C()

    t <= A <= [B,C]

    assert t._getTree() == {
        t:[ {A: [{B:[]},{C:[]}]}]
    }


    # And now A is a placeholder
    t=Tag.body()

    A= Tag()
    B= Tag.B()
    C= Tag.C()

    t <= A <= [B,C]
    # assert t._getTree() == {        # A is cleared from the tree
    #     t:[{B:[]},{C:[]}]
    # }
    assert t._getTree() == {          # A is in the tree
        t:[ {A: [{B:[]},{C:[]}]}]
    }


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
    # r=await hr.interact(0,None,None,None,None)

    assert f'<body id="{id(hr.tag)}">hello</body>' in str(hr)


def test_placeholder_mod_guess():

    t=Tag.body()

    A= Tag()
    B= Tag.B()
    C= Tag.C()

    t <= A <= [B,C]

    s=Stater(t)

    print("BEFORE:",t)
    # A.clear()
    A<="hllll"
    print("AFTER: ",t)

    mod = s.guess()

    # IT SHOULD BE LIKE THIS !!!!!
    # IT SHOULD BE LIKE THIS !!!!!
    # IT SHOULD BE LIKE THIS !!!!!
    assert mod == [t]   # body has changed !
    # IT SHOULD BE LIKE THIS !!!!!
    # IT SHOULD BE LIKE THIS !!!!!
    # IT SHOULD BE LIKE THIS !!!!!


if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    logging.getLogger("htag.tag").setLevel( logging.ERROR )

    # test_base()
    # test_tree()
    # test_at_construction()
    # asyncio.run( test_placeholder_to_body() )
    # asyncio.run( test_using_a_placeholder() )

    test_placeholder_mod_guess()