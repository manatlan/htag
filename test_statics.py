from htag import H,Tag,HTagException
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
        statics=H.style("/*S1*/")

    assert "/*S1*/" in str(HRenderer( O, "//"))
    ################################################################
    class OO1(Tag.div):
        imports = O
        def init(self):
            self <= O() # "O" is a direct child

    assert "/*S1*/" in str(HRenderer( OO1, "//"))
    ################################################################
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
        statics=H.style("/*S1*/")

    assert "/*S1*/" in str(HRenderer( O, "//"))
    ################################################################
    class OO1(Tag.div):
        imports = O
        def render(self):
            self <= O() # "O" is a direct child

    assert "/*S1*/" in str(HRenderer( OO1, "//"))
    ################################################################
    class OO2(Tag.div):
        imports = O
        def render(self):
            self <= Tag.div( O() ) # "O" is a non-direct child

    assert "/*S1*/" in str(HRenderer( OO2, "//"))
    ################################################################

def test_TagBase_md5():

    sameContent="hello"
    sameattrs=dict(_class="hello")
    t1=H.a(sameContent,**sameattrs)
    t2=H.a(sameContent,**sameattrs)

    assert t1.md5 == t2.md5

def test_Tag_md5():
    class My(Tag.div):
        def __init__(self,txt,**a):
            Tag.div.__init__(self,**a)
            self <= txt

    sameContent="hello"
    sameattrs=dict(_class="hello")
    t1=My(sameContent,**sameattrs)
    t2=My(sameContent,**sameattrs)

    #md5 is computed, but not useful
    #(as it's only for tagbase in statics)
    assert t1.md5 != t2.md5 # so, it's different


if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)
    # test_Tag_md5()
    test_statics_only_tagbase()