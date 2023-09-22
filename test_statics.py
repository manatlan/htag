from htag import Tag,HTagException
from htag.render import HRenderer
import pytest

def test_statics_only_tagbase():
    class AEFF(Tag):
        statics="body {background:red}", b"alert(42);"

    h=str(HRenderer(AEFF,"//js"))

    assert "<style>body {background:red}</style>" in h
    assert "<script>alert(42);</script>" in h

    del AEFF


def test_built_immediatly():
    ################################################################
    # test static discovering (in built immediatly)
    ################################################################
    class O(Tag.div):
        statics=Tag.style("/*S1*/")

    assert "/*S1*/" in str(HRenderer( O, "//"))
    ################################################################
    class OO1(Tag.div):
        imports = O
        def init(self):
            self <= O() # "O" is a direct child

    assert "/*S1*/" in str(HRenderer( OO1, "//"))
    # ################################################################
    class OO2(Tag.div):
        imports = O
        def init(self):
            self <= Tag.div( O() ) # "O" is a non-direct child

    assert "/*S1*/" in str(HRenderer( OO2, "//"))
    ################################################################

def test_build_lately():
    ################################################################
    # test static discovering (in built lately)
    ################################################################
    class O(Tag.div):
        statics=Tag.style("/*S1*/")

    assert "/*S1*/" in str(HRenderer( O, "//"))
    ################################################################
    class OO1(Tag.div):
        imports = O
        def render(self):
            self.clear()
            self <= O() # "O" is a direct child

    assert "/*S1*/" in str(HRenderer( OO1, "//"))
    ################################################################
    class OO2(Tag.div):
        imports = O
        def render(self):
            self.clear()
            self <= Tag.div( O() ) # "O" is a non-direct child

    assert "/*S1*/" in str(HRenderer( OO2, "//"))
    ################################################################

# def test_TagBase_md5():

#     sameContent="hello"
#     sameattrs=dict(_class="hello")
#     t1=Tag.a(sameContent,**sameattrs)
#     t2=Tag.a(sameContent,**sameattrs)

#     assert t1.md5 == t2.md5

# def test_Tag_md5():
#     class My(Tag.div):
#         def __init__(self,txt,**a):
#             Tag.div.__init__(self,**a)
#             self <= txt

#     sameContent="hello"
#     sameattrs=dict(_class="hello")
#     t1=My(sameContent,**sameattrs)
#     t2=My(sameContent,**sameattrs)

#     #md5 is computed, but not useful
#     #(as it's only for tagbase in statics)
#     assert t1.md5 != t2.md5 # so, it's different

def test_doubbles_statics():
    class AppSS(Tag.div):
        statics = "kiki","kiki"
        imports=[] # just to avoid import all Tag in the scoped process
        def init(self,m="default"):
            self <= m
            self <= Tag.span("world")

    hr1=HRenderer(AppSS,"")
    assert len(hr1._statics)==2                      # 2 real statics
    assert str(hr1).count("<style>kiki</style>")==1  # but just one rendered (coz they are identicals (_hash_))

    class AppST(Tag.div):
        statics = Tag.style("kiki"),Tag.style("kiki")
        imports=[] # just to avoid import all Tag in the scoped process
        def init(self,m="default"):
            self <= m
            self <= Tag.span("world")

    hr2=HRenderer(AppST,"")
    assert len(hr2._statics)==2                      # 2 real statics
    assert str(hr2).count("<style>kiki</style>")==1  # but just one rendered (coz they are identicals (_hash_))

def test_inherit_bases():
    class A(Tag):
        statics = "StylesA"
        imports=[]

    class B(A):
        statics = "StylesB"
        imports=[]

    hr=HRenderer(A,"")
    styles=[i for i in hr._statics if i.tag=="style"]
    assert len(styles)==1

    hr=HRenderer(B,"")
    styles=[i for i in hr._statics if i.tag=="style"]
    assert len(styles)==2


if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
    # test_Tag_md5()
    # test_statics_only_tagbase()
    test_built_immediatly()