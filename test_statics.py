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