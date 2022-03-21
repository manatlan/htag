from htag import Tag
from htag.render import HRenderer

def test_built_immediatly():
    ################################################################
    # test static discovering (in built immediatly)
    ################################################################
    class O(Tag):
        statics=Tag.style("/*S1*/")

    assert "/*S1*/" in str(HRenderer( O(), "//"))
    ################################################################
    class OO(Tag):
        def __init__(self):
            Tag.__init__(self)
            self <= O() # "O" is a direct child

    assert "/*S1*/" in str(HRenderer( OO(), "//"))
    ################################################################
    class OO(Tag):
        def __init__(self):
            Tag.__init__(self)
            self <= Tag.div( O() ) # "O" is a non-direct child

    assert "/*S1*/" in str(HRenderer( OO(), "//"))
    ################################################################

def test_build_lately():
    ################################################################
    # test static discovering (in built lately)
    ################################################################
    class O(Tag):
        statics=Tag.style("/*S1*/")

    assert "/*S1*/" in str(HRenderer( O(), "//"))
    ################################################################
    class OO(Tag):
        def __str__(self):
            self <= O() # "O" is a direct child
            return str(super())

    assert "/*S1*/" in str(HRenderer( OO(), "//"))
    ################################################################
    class OO(Tag):
        def __str__(self):
            self <= Tag.div( O() ) # "O" is a non-direct child
            return str(super())

    assert "/*S1*/" in str(HRenderer( OO(), "//"))
    ################################################################

def test_TagBase_md5():

    sameContent="hello"
    sameattrs=dict(_class="hello")
    t1=Tag.a(sameContent,**sameattrs)
    t2=Tag.a(sameContent,**sameattrs)

    assert t1.md5 == t2.md5

def test_Tag_md5():
    class My(Tag):
        def __init__(self,txt,**a):
            Tag.__init__(self,**a)
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