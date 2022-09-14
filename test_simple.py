#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
import pytest

from htag import H,Tag,HTagException

anon=lambda t: str(t).replace( str(id(t)),"<id>" )

################################################################################################################
def test_base():
    assert str(H.div()) == "<div></div>"
    assert str(H.div(None)) == "<div></div>"
    assert str(H.div([])) == "<div></div>"
    assert str(H.div("hello")) == "<div>hello</div>"
    assert str(H.div([1,2,3])) == "<div>123</div>"
    assert str(H.my_div("test")) == "<my-div>test</my-div>"

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

    d=H.div( gen() )
    assert str(d) == "<div>012</div>"

# def test_ko():
    # with pytest.raises(HTagException):
    #     H() #explicitly forbiddent

    # with pytest.raises(HTagException):
    #     H.span(no="kk")

# def test_H():
#     # Tag.H is special, it's a shortcut to H
#     assert  Tag.H == H
#     assert  not issubclass(Tag.H, Tag)

#     # ensure constructor, constructs well
#     assert  issubclass(Tag.H.div, TagBase)
#     assert  not issubclass(Tag.H.div, Tag)

#     #whereas Tag.<> is dynamic (with @id), and inherit boths
#     assert  issubclass(Tag.div, TagBase)
#     assert  issubclass(Tag.div, Tag)

#     #the main diff ... Tag.H.<> has no @id
#     assert "id=" not in str(Tag.H.span("hello",_class="hello"))
#     #whereas ... Tag.<> has an @id
#     assert "id=" in str(Tag.span("hello",_class="hello"))

#     # it's the same construction
#     assert str(Tag.H.span("hello",_class="hello")) == str(H.span("hello",_class="hello"))

def test_attrs():
    d=Tag.div(_data_text=12)
    assert d["data-text"]==12

    assert d.attrs == {"data-text":12}
    d["data-text"]+=1
    assert str(d) == '<div data-text="13"></div>'

    d=Tag.div(_checked=True)
    assert d["checked"]
    assert d.attrs == {"checked":True}
    assert str(d) == '<div checked></div>'

    d=Tag.div(_checked=False)
    assert not d["checked"]
    assert d.attrs == {"checked":False}
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

def test_childs():
    t = Tag.ul()
    t <= Tag.li()
    assert len(t.childs)==1
    assert t.childs[0].tag == "li"

    t.childs.append( Tag.li() )
    assert len(t.childs)==2
    assert t.childs[-1].tag == "li"

    t.clear()
    assert len(t.childs)==0

    t <= [Tag.li(),Tag.li()]
    assert len(t.childs)==2

    t <= (Tag.li(),Tag.li())
    assert len(t.childs)==4

    del t.childs[2]
    assert len(t.childs)==3

    t.set( Tag.li() )
    assert len(t.childs)==1




def test_tag_generation_with_opt_params():
    class NewTag(Tag.h1):

        def __init__(self,nb,txt="torchon", **a):
            Tag.__init__(self, **a)
            self.nb=nb
            self.txt=txt
            # self["class"]="12"
            for i in range(1,self.nb+1):
                self.add( H.li(f"{i} {self.txt}",_id=i) )

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
         '''<h1 class="jo" style="border:1px solid red;" id="<id>"><li id="1">1 torchon</li><li id="2">2 torchon</li><li id="3">3 torchon</li></h1>'''

    g=NewTag(3,txt="serviette",_class="jo",_style="border:1px solid red")
    assert anon(g) == \
        '''<h1 class="jo" style="border:1px solid red;" id="<id>"><li id="1">1 serviette</li><li id="2">2 serviette</li><li id="3">3 serviette</li></h1>'''


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

    bc=c.bind.onclick(12)
    assert bc.instance == c
    assert bc.mname == "onclick"
    assert bc.args == (12,)
    assert bc.kargs == {}
    js=str(bc)
    assert 'interact( {"id": <id>, "method": "onclick", "args": [12], "kargs": {}, "event": jevent(event)} )' in js.replace( str(id(c)),"<id>" )


def test_generate_real_js():

    class NewTag(Tag.div):
        def __init__(self,**a):
            Tag.div.__init__(self,**a)
            self.add( H.button( "width?",_onclick=self.bind.test( "width", b"window.innerWidth") ))

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

# def test_its_the_same_tagbase_exactly():

#     class Test2(TagBase):
#         def __init__(self):
#             TagBase.__init__(self)
#             self.tag="h1"
#             self <= "hello"
#             self["id"] = 42

#     class Test3(H.h1):
#         def __init__(self):
#             Tag.h1.__init__(self)
#             self <= "hello"
#             self["id"] = 42

#     t1 = H.h1("hello",_id=42)
#     t2 = Test2()
#     t3 = Test3()

#     assert str(t1) == str(t2) == str(t3)
#     assert t1._getStateImage() == t2._getStateImage() == t3._getStateImage()


# def test_base_concepts():
#     # Build a TagBase
#     o=H.h1("yo",_class="ya")
#     assert isinstance(o, TagBase)
#     assert not isinstance(o, Tag)
#     assert str(o) == '<h1 class="ya">yo</h1>'

#     # build a tag
#     o=Tag.h1( _class="ya")
#     o<= "yo"
#     assert isinstance(o, TagBase)
#     assert isinstance(o, Tag)
#     assert anon(o) == '<h1 class="ya" id="<id>">yo</h1>'


#     # INHERIT A REAL TAG
#     class Nimp2(Tag.h2):

#         def __init__(self,name,**attrs):
#             Tag.h2.__init__(self,**attrs)
#             self["name"] = name
#             self <= H.div(name)

#     o=Nimp2("yo",_class="ya")
#     print( type(o),o.__class__,o )
#     assert isinstance(o, TagBase)
#     assert isinstance(o, Tag)
#     assert anon(o) == '<h2 class="ya" id="<id>" name="yo"><div>yo</div></h2>'


def test_state_yield():
    class TEST(Tag.div):
        def __init__(self):
            super().__init__()
            self <= Tag.button("go", _onclick=self.bind.test())

        def test(self):
            self.clear()
            self <= H.h1("hello1")
            self("/*JS1*/")
            yield
            self.clear()
            self <= H.h1("hello2")
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

def test_auto_instanciate_attributs():
    class My(Tag):
        js="/*js1*/"

    t=My()
    assert t.js == "/*js1*/"

    t=My(js="/*js2*/")  # here, we override self.js ;-)
    assert t.js == "/*js2*/"

    t=My(value=42)      # here we create a new attribut (avoid to create an __init__ for that)
    assert t.js == "/*js1*/"
    assert t.value == 42


def test_iadd():
    B=Tag.H.B()
    C=Tag.H.C()


    # same concept "<=" & "+="
    a1=Tag.H.A()
    a1 <= B
    a1 <= C

    a2=Tag.H.A()
    a2 += B
    a2 += C

    a3=Tag.H.A()
    a3.add( B )
    a3.add( C )

    assert str(a1)==str(a3)==str(a2)


    # but not with "tuple"
    a1=Tag.H.A()
    a1 <= B, C  # it's not a tuple (it's 2 statements)

    a2=Tag.H.A()
    a2 += B, C  # it's a tuple

    assert str(a1) != str(a2)
    assert str(a1) == "<A><B></B></A>"
    assert str(a2) == "<A><B></B><C></C></A>"


    # btw, This is possible ... '<=' is chain'able
    a1=Tag.H.A()
    a1 <= B <= C <= 12
    assert str(a1) == "<A><B><C>12</C></B></A>"

    # but syntax error, for that
    ## a1 += B += C


    # AVOID TO DO SOMETHING LIKE THAT
    # AVOID TO DO SOMETHING LIKE THAT
    # AVOID TO DO SOMETHING LIKE THAT
    # and it could be weird to mix them like that
    a=Tag.H.A()
    B=Tag.H.B()
    C=Tag.H.C()
    a += B <= C # '<=' is first, and return C ... so A will contain just C ... B is lost in the deep ;-(
    assert str(a) == "<A><C></C></A>"
    # AVOID TO DO SOMETHING LIKE THAT
    # AVOID TO DO SOMETHING LIKE THAT
    # AVOID TO DO SOMETHING LIKE THAT

    # "<=" return the added, so it could be chained (a<=b<=c)
    # "+=" can add mass object using a tuple form (without braces) ( a += b,c,d,e  ===  a <= (b,c,d,e) )
    a1=Tag.H.A()
    b=Tag.H.B()
    c=Tag.H.C()
    a1+= b,c

    a2=Tag.H.A()
    b=Tag.H.B()
    c=Tag.H.C()
    a2<= (b,c)

    a3=Tag.H.A()
    b=Tag.H.B()
    c=Tag.H.C()
    a3<= b+c

    a4=Tag.H.A()
    b=Tag.H.B()
    c=Tag.H.C()
    a4+= b+c

    assert str(a1)==str(a2)==str(a3)==str(a4)



def test_add():
    a=Tag.H.A()
    b=Tag.H.B()
    c=Tag.H.C()

    assert 42+a == [42,a]
    assert a+None == None+a == [a]

    x=a+b+c
    assert x==[a,b,c]

    x=a+42
    assert x==[a,42]

    x=42+a
    assert x==[42,a]

    a=Tag.H.A()
    b=Tag.H.B()
    c=Tag.H.C()

    a.clear()
    a <= b+c+c+c
    assert str(a) == "<A><B></B><C></C><C></C><C></C></A>"

    a.clear()
    a<= b+"kkk"+42+None+78
    assert str(a) == "<A><B></B>kkk4278</A>"

    # a.clear()
    # a+= b+"kkk"+42+None+78
    # print(a)

    a.clear()
    a.add( b+"kkk"+42+None+78 )
    assert str(a) == "<A><B></B>kkk4278</A>"

    a.childs.append( c )
    assert str(a) == "<A><B></B>kkk4278<C></C></A>"

    x=12+(a+c)+(b+c)
    assert x == [12,a,c,b,c]

    xx=12+a+(c+b)+c
    assert xx == [12,a,c,b,c]

    x1=xx[:]
    x1+=13+c
    assert x1 == [12,a,c,b,c,13,c]

    x1=xx[:]
    x1+=[13,c]
    assert x1 == [12,a,c,b,c,13,c]

    x1=xx[:]
    x1+=(13,c)
    assert x1 == [12,a,c,b,c,13,c]


    a=Tag.H.A()
    c=Tag.H.C()
    a+=c
    assert str(a) == "<A><C></C></A>"


def test_js_call_at_init():

    class HRSimu():
        def _addInteractionScript(self,js):
            self.ijs=js

    class TEST(Tag.div):
        js="/*JS2*/"
        def init(self):
            self("/*JS1*/") # <= only in interaction, for now

    # It doesn't crash now !
    # (but the interaction script is forgotten)
    TEST()

    # NOW WORKS !!!!
    myhr=HRSimu()
    x=TEST(hr=myhr)
    assert "/*JS1*/" in myhr.ijs

    assert "/*JS2*/" in x._getAllJs()[0]  # normal, coz it's an interaction script, not a static js


def test_init_hr():
    class A(Tag.div):
        pass
    class TEST(Tag.div):
        def init(self):
            self <= A()
            self <= A()+A()+"hello"

    t=TEST( hr="FAKE_HR" ) # simulate the hr which is setted by HRenderer IRL
    assert t._hr=="FAKE_HR"
    assert t.parent==None
    assert len(t.childs) == 4
    assert len([i for i in t.childs if isinstance(i,Tag)]) == 3
    assert all( [i.parent==t for i in t.childs if isinstance(i,Tag)] )

def test_remove():
    t=Tag.div()
    o=Tag.b("hello")
    t<=o
    assert len(t.childs)==1
    assert o in t.childs
    assert t.remove(o)
    assert len(t.childs)==0
    assert o not in t.childs
    assert not t.remove(o)

    t.add("a")
    t.add("a")
    assert len(t.childs)==2
    assert "a" in t.childs
    assert t.remove("a")
    assert len(t.childs)==1
    assert "a" in t.childs
    assert t.remove("a")
    assert len(t.childs)==0

    o=Tag.b("hello")
    assert not o.remove()
    t<=o
    assert len(t.childs)==1
    assert o in t.childs
    assert o.remove()
    assert len(t.childs)==0


def test_innerHTML():
    # normal case
    t=Tag.div()
    assert t.innerHTML==""
    o=Tag.b("hello")
    t.add(o)
    assert "<b>" in str(t)
    assert "<b>" in t.innerHTML

    # But ensure that with tagbase(H), it keeps the @id
    t=Tag.div()
    assert t.innerHTML==""
    o=Tag.b("hello",_id="myb")
    t.add(o)
    assert "<b id=" in str(t)
    assert "<b id=" in t.innerHTML

    t=Tag.div(42)
    assert t.innerHTML=="42"


def test_elements_to_str():
    l=Tag.H.div("hello")+Tag.H.div("world")
    assert str(l) == "<div>hello</div><div>world</div>"
    l=Tag.H.div("hello")+42
    assert str(l) == "<div>hello</div>42"
    l=42+Tag.H.div("hello")
    assert str(l) == "42<div>hello</div>"

if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)

    # test_base()
    # test_ko()
    test_attrs()
    # test_bad_tag_instanciation()
    # test_tag_generation_with_opt_params()
    # test_tag_generation_override_attr_at_construct()
    # test_generate_js_interact()
    # test_generate_real_js()
    # test_its_the_same_tagbase_exactly()

    # test_base_concepts()
    # test_iadd()
    # test_js_call_at_init()
    # test_init_hr()
    # test_remove()
    # test_innerHTML()
    # test_elements_to_str()