#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import pytest

from htag import Tag,HTagException
from htag.tag import TagBase

anon=lambda t: str(t).replace( str(id(t)),"<id>" )

################################################################################################################
def test_base():
    assert str(Tag.div()) == "<div></div>"
    assert str(Tag.div(None)) == "<div></div>"
    assert str(Tag.div([])) == "<div></div>"
    assert str(Tag.div("hello")) == "<div>hello</div>"
    assert str(Tag.div([1,2,3])) == "<div>123</div>"
    assert str(Tag.my_div("test")) == "<my-div>test</my-div>"

def test_base2():
    d=Tag.div("hello")
    assert str(d) == "<div>hello</div>"
    d.set("world")
    assert str(d) == "<div>world</div>"
    d.set( ("hello","world"))
    assert str(d) == "<div>helloworld</div>"
    d.set( ["hello","world"])
    assert str(d) == "<div>helloworld</div>"
    d.set(None) # like clear()
    assert str(d) == "<div></div>"

    def gen():
        for i in range(3):
            yield i
    d=Tag.div()
    d.add( gen() )
    assert str(d) == "<div>012</div>"
    d.set( gen() )
    assert str(d) == "<div>012</div>"

    d.clear()
    d <= gen()
    assert str(d) == "<div>012</div>"

    d=Tag.div( gen() )
    assert str(d) == "<div>012</div>"

def test_ko():
    with pytest.raises(HTagException):
        Tag.span(no="kk")


def test_attrs():
    d=Tag.div(_data_text=12)
    assert d["data-text"]==12
    d["data-text"]+=1
    assert str(d) == '<div data-text="13"></div>'

    d=Tag.div(_checked=True)
    assert d["checked"]
    assert str(d) == '<div checked></div>'

    d=Tag.div(_checked=False)
    assert not d["checked"]
    assert str(d) == '<div></div>'

    d=Tag.my_div( "hello")
    assert str(d) == "<my-div>hello</my-div>"

    d=Tag.div(_id="d1",_class="click")
    assert d["id"]=="d1"
    assert d["class"]=="click"
    assert str(d) == '<div id="d1" class="click"></div>'

    d=Tag.div( "hello")
    d.clear()
    d.add("bye")
    d.add("bye")
    assert str(d) == "<div>byebye</div>"

    div=Tag.div("hello",_style="border:1px solid red")
    div["id"] = "mydiv"
    div.add(Tag.h1("world"))





def test_bad_tag_instanciation():
    class NewTag(Tag):
        tag="h1"

    with pytest.raises(TypeError):
        NewTag(2)

def test_tag_generation_with_opt_params():
    class NewTag(Tag.h1):

        def __init__(self,nb,txt="torchon", **a):
            print("===",self.tag)
            Tag.__init__(self, **a)
            self.nb=nb
            self.txt=txt
            # self["class"]="12"
            for i in range(1,self.nb+1):
                self.add( Tag.li(f"{i} {self.txt}",_id=i) )

    # can't set an html attribut id
    with pytest.raises(HTagException):
        NewTag(2,_id=12313213)

    # but can set an attribut on instance
    x=NewTag(2,id=12313213)
    assert x.id==12313213
    assert x["id"] == id(x) # it's a real htag.tag, so it got a real html attribut

    # can set attributs
    x=NewTag(2,param1="jiji",param2=42)
    assert x.param1=="jiji"
    assert x.param2==42

    # test bad calls
    with pytest.raises(TypeError):
        NewTag(2,"kkk","oo",param1="jiji")
    with pytest.raises(TypeError):
        NewTag()

    g=NewTag(3,_class="jo",_style="border:1px solid red")
    assert g["id"] == id(g)

    assert anon(g) == \
         '''<h1 class="jo" style="border:1px solid red" id="<id>"><li id="1">1 torchon</li><li id="2">2 torchon</li><li id="3">3 torchon</li></h1>'''

    g=NewTag(3,txt="serviette",_class="jo",_style="border:1px solid red")
    assert anon(g) == \
        '''<h1 class="jo" style="border:1px solid red" id="<id>"><li id="1">1 serviette</li><li id="2">2 serviette</li><li id="3">3 serviette</li></h1>'''


def test_tag_generation_override_attr_at_construct():
    class NewTag(Tag.h1):
        tag="h1"

        def __init__(self,**a):
            Tag.__init__(self,**a)
            self["class"]="classA"

    g=NewTag()
    assert anon(g) == '<h1 id="<id>" class="classA"></h1>'

    g=NewTag()
    g["class"]="classB"
    assert anon(g) == '<h1 id="<id>" class="classB"></h1>'

    g=NewTag(_class="classB")
    assert anon(g) == '<h1 class="classA" id="<id>"></h1>' #TODO: should be classB ... no ? -> adapt



def test_generate_js_interact():

    class NewTag(Tag):
        tag="div"

        def init(self,value=0):
            self.nb=value
            self.update()

        def update(self): # special method
            self.clear()
            self.add( Tag.button( "-",_onclick=self.bind.onclick(-1) ))
            self.add( self.nb )
            self.add( Tag.button( "+",_onclick=self.bind.onclick(1) ))
            for i in range(self.nb):
                self.add("*")

        def onclick(self,v):
            self.nb+=v
            self.update()

    c=NewTag()

    with pytest.raises(HTagException):
        c.bind.onclick_unknown(12)

    js=c.bind.onclick(12)
    print(js)
    assert js.replace( str(id(c)),"<id>" ) == 'interact( {"id": <id>, "method": "onclick", "args": [12], "kargs": {}} );'


def test_generate_real_js():

    class NewTag(Tag):
        def __init__(self,**a):
            Tag.__init__(self,**a)
            self.add( Tag.button( "width?",_onclick=self.bind.test( "width", b"window.innerWidth") ))

        def test(self,txt,width):
            print(txt,"=",width)

    c=NewTag()
    assert "&quot;args&quot;: [&quot;width&quot;, window.innerWidth], &quot;kargs&quot;: {}" in str(c)

    assert hasattr(c,"exit")
    c.exit()    # does nothing ;-)

    class Kiki(NewTag): # INHERIT (it's the same)
        pass

    clone = Kiki()
    assert str(c).replace( str(id(c)), str(id(clone)) ) == str(clone)   # same, modulo id !

def test_its_the_same_tagbase_exactly():

    class Test2(TagBase):
        def __init__(self):
            TagBase.__init__(self)
            self.tag="h1"
            self <= "hello"
            self["id"] = 42

    class Test3(Tag.h1):
        def __init__(self):
            Tag.h1.__init__(self)
            self <= "hello"
            self["id"] = 42

    t1 = Tag.h1("hello",_id=42)
    t2 = Test2()
    t3 = Test3()

    assert str(t1) == str(t2) == str(t3)
    assert t1._getStateImage() == t2._getStateImage() == t3._getStateImage()


def test_base_concepts():
    # Build a TagBase
    o=Tag.h1("yo",_class="ya")
    assert isinstance(o, TagBase)
    assert not isinstance(o, Tag)
    assert str(o) == '<h1 class="ya">yo</h1>'

    # build a tag
    o=Tag( _class="ya")
    o.tag="h1"
    o<= "yo"
    assert isinstance(o, TagBase)
    assert isinstance(o, Tag)
    assert anon(o) == '<h1 class="ya" id="<id>">yo</h1>'


    # INHERIT A REAL TAG
    class Nimp2(Tag):
        tag="h2"

        def __init__(self,name,**attrs):
            Tag.__init__(self,**attrs)
            self["name"] = name
            self <= Tag.div(name)

    o=Nimp2("yo",_class="ya")
    print( type(o),o.__class__,o )
    assert isinstance(o, TagBase)
    assert isinstance(o, Tag)
    assert anon(o) == '<h2 class="ya" id="<id>" name="yo"><div>yo</div></h2>'


def test_state_yield():
    class TEST(Tag):
        tag="div"

        def __init__(self):
            super().__init__()
            self <= Tag.button("go", _onclick=self.bind.test())

        def test(self):
            self.clear()
            self <= Tag.h1("hello1")
            self("/*JS1*/")
            yield
            self.clear()
            self <= Tag.h1("hello2")
            self("/*JS2*/")

    s=TEST()

    jss=[]
    TEST.__call__=lambda self,js: jss.append(js)
    for i in s.test():
        assert "<h1>hello1</h1>" in str(s)
        assert jss.pop()=="/*JS1*/" and len(jss)==0

    # state of the instance has changed
    assert "<h1>hello2</h1>" in str(s)
    assert jss.pop()=="/*JS2*/" and len(jss)==0

# test_base()
# test_ko()
# test_attrs()
# test_bad_tag_instanciation()
# test_tag_generation_with_opt_params()
# test_tag_generation_override_attr_at_construct()
# test_generate_js_interact()
# test_generate_real_js()
# test_its_the_same_tagbase_exactly()

# test_base_concepts()
