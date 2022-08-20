import pytest


from htag import Tag,HTagException
from htag.attrs import StrClass,StrStyle
from htag.tag import NotBindedCaller

def test_StrClass():
    classe = StrClass("  click  main  kik34 ")
    # classe = StrClass()
    assert classe=="click main kik34"

    classe.toggle("toto")
    assert classe=="click main kik34 toto"
    classe.toggle("toto")
    assert classe=="click main kik34"
    classe.add("c1","c2")
    assert classe=="click main kik34 c1 c2"
    classe.remove("c1","main","click")
    assert classe=="kik34 c2"
    classe.remove("NIMP","kik34")
    assert classe=="c2"

    # old classic way, still works
    classe=classe+" koko"
    assert classe=="c2 koko"
    classe="koko2 "+classe
    assert classe=="koko2 c2 koko"

def test_StrStyle():
    style= StrStyle("Background: yellow !important;pointer:mouse")
    style.set(" border "," 1px solid red ")
    assert style == "background:yellow !important;pointer:mouse;border:1px solid red;"

    style.remove("pointer")
    assert style=="background:yellow !important;border:1px solid red;"
    print(style.dict)
    assert style.dict == {'background': 'yellow !important', 'border': '1px solid red'}

    assert style.get("BackGround ") == ['yellow !important']
    assert style.contains(" bACKground ")
    assert "BackgRound" in style
    assert not style.contains("nimp")
    assert "nimp" not in style

    # old classic way, still works
    style= style+"titi:tata"
    assert style=="background:yellow !important;border:1px solid red;titi:tata;"

    assert style.dict=={'background': 'yellow !important', 'border': '1px solid red', 'titi': 'tata'}
    assert "titi" in style.dict.keys()
    style.dict["pointer"]="cursor"
    assert style.dict=={'background': 'yellow !important', 'border': '1px solid red', 'titi': 'tata', 'pointer':'cursor'}

    # old classic way, still works
    style= ";;;titi2:tata2;;;"+ style
    assert style=="titi2:tata2;background:yellow !important;border:1px solid red;titi:tata;pointer:cursor;"


def test_StrStyle_multiple():
    style= StrStyle("background: red;backGround: black")
    assert style.contains("BackGround") == 2
    assert len(style)==2
    assert len(style.dict)==1
    assert "bACKground" in style
    assert style.get("background") == ["red","black"]
    style.set("background","yellow") # in fact, it "add"ing ;-)
    assert style.get("background") == ["red","black","yellow"]
    style+="background: purple" # add, in the classic way
    assert style.get("background") == ["red","black","yellow","purple"]
    style.remove("backgrounD")
    assert style.get("bacKground") == []
    assert style==""

    style= StrStyle("background: red;backGround: black")
    assert style.contains("BackGround") == 2
    assert style.get("background") == ["red","black"]
    style.set("background","yellow",True) # now, it's make it unique
    assert style.get("bacKground") == ["yellow"]

    style= StrStyle("background: red;backGround: black")
    assert style.get("background") == ["red","black"]
    style.set("background","yellow") # in fact, it "add"ing ;-)

    # in "style.dict", it's a real dict (and only the last one will be here)
    assert style.get("background") == ["red","black","yellow"]
    assert style.dict == {'background': 'yellow'}

    # to be really sure ;-)
    assert style.get("background") == ["red","black","yellow"]
    assert style.dict == {'background': 'yellow'}

    style.dict.clear()
    assert style.dict == {}
    assert style.get("bAckground") == []
    assert style==""

    style.dict.update( dict(kiki="koko"))
    assert style.dict == {"kiki":"koko"}

def test_tag_class():
    # test a constructor with a _class
    d=Tag.div( "toto", _class="myclass")
    assert d["class"].contains("myclass")
    assert "myclass" in d["class"]
    assert len(d["class"])==1
    assert d["class"] == "myclass"
    d["class"].add("kiki")
    assert d["class"] == "myclass kiki"
    assert len(d["class"])==2

    # test a constructor with a _class (python's list)
    d=Tag.div( "toto", _class=["myclass"])
    assert d["class"].contains("myclass")
    assert d["class"] == "myclass"
    d["class"].add("kiki")
    assert d["class"] == "myclass kiki"

    # python's list
    assert d["class"].list == ["myclass", "kiki"]
    d["class"].list.append("koko")
    assert d["class"] == "myclass kiki koko"
    d["class"].list.clear()
    assert d["class"] == ""
    assert "class" not in str(d)
    assert len(d["class"])==0

    # test a constructor without a _class
    d=Tag.div( "toto" )
    assert not d["class"].contains("kiki")
    d["class"].add("kiki")
    d["class"].add("kiki")
    d["class"].add("kiki")
    assert d["class"] == "kiki"
    d["class"].toggle("kiki")
    assert d["class"] == ""
    assert "class" not in str(d)

def test_tag_style():
    # test a constructor with a _style
    d=Tag.div( "toto", _style="background: red")
    assert d["style"] == "background:red;"
    d["style"].set("border-radius", "4px")
    assert d["style"] == "background:red;border-radius:4px;"

    # test a constructor with a _style (python's dict)
    d=Tag.div( "toto", _style=dict(background="red") )
    assert d["style"] == "background:red;"
    assert d["style"].dict == {'background': 'red'}

    # test a constructor without a _style
    d=Tag.div( "toto" )
    assert d["style"]==""
    assert d["style"].dict=={}


def test_non_null_attrs():
    t=Tag.div()
    assert t["class"] is not None
    assert t["style"] is not None

    # all starts with "on" are not None
    assert t["onclick"] is not None
    assert t["on_nimp"] is not None

    # all others are none
    assert t["kiki"] is None

    assert isinstance( t["class"] ,StrClass )
    assert isinstance( t["style"] ,StrStyle )
    assert isinstance( t["onclick"] ,NotBindedCaller )
    assert isinstance( t["onUNKNOWN"] ,NotBindedCaller )

def test_non_null_onevent():
    def method(o):
        pass
    t=Tag.div()
    assert "onunknown" not in str(t)    # stupid fact

    t["onUNKNOWN"].bind( method )
    assert "onunknown" in str(t)

if __name__=="__main__":
    # test_StrClass()
    # test_StrStyle()
    # test_tag_class()
    # test_tag_style()
    # test_StrStyle_multiple()
    #test_non_null_attrs()
    test_non_null_onevent()