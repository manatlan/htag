from htag import Tag,HTagException
import pytest

def test_base():
    t=Tag.div()
    assert t.parent == None
    assert t.root == t


def test_adding_None():
    parent = Tag.div()
    parent.add(None)        # does nothing !
    parent <= None          # does nothing !
    parent += None          # does nothing !
    parent += [None,None]   # does nothing !
    assert len(parent.childs)==0

def test_try_to_override_important_props():
    t = Tag.div()
    with pytest.raises( AttributeError ):
        t.parent=None

    with pytest.raises( AttributeError ):
        t.root=None

    with pytest.raises( AttributeError ):
        t.event=None


def test_unparenting_remove():
    parent = Tag.div()
    child = Tag.span()
    childchild = Tag.b()

    parent <= child <= childchild
    assert str(parent)=="<div><span><b></b></span></div>"
    assert child.root == childchild.root == parent.root == parent

    assert child.parent == parent
    assert childchild.parent == child
    assert parent.childs[0] == child

    child.remove()
    assert str(parent)=="<div></div>"

    assert len(parent.childs) == 0
    assert child.parent == None
    assert childchild.parent == child

    assert parent.root == parent
    assert child.root == child
    assert childchild.root == child

def test_unparenting_clear():
    parent = Tag.div()
    child = Tag.span()
    childchild = Tag.b()

    parent <= child <= childchild
    assert str(parent)=="<div><span><b></b></span></div>"
    assert child.root == childchild.root == parent.root == parent

    parent.clear()
    assert str(parent)=="<div></div>"

    assert len(parent.childs) == 0
    assert child.parent == None
    assert childchild.parent == child

    assert parent.root == parent
    assert child.root == child
    assert childchild.root == child


def test_cant_add_many_times():
    parent1 = Tag.div()
    parent2 = Tag.div()

    parent1.STRICT_MODE=True
    parent2.STRICT_MODE=True


    a_child = Tag.span()
    parent1 += a_child

    # can't be added to another one
    with pytest.raises(HTagException):
        parent2 += a_child

    assert a_child.parent == parent1

    # clear parent1
    parent1.clear()

    # so the child is no more in parent1
    # we can add it to parent2
    parent2 += a_child
    assert a_child.parent == parent2

#####################################################################
#####################################################################
#####################################################################
def t0():
    parent = Tag.div()
    a_child = Tag.span()

    parent.add( a_child, True)  # force reparent
    parent.add( a_child, True)  # force reparent

def t00():
    parent = Tag.div()
    a_child = Tag.span()

    parent.add( a_child, False)  # don't force reparent (default)
    parent.add( a_child, False)  # don't force reparent (default)

def t1():
    parent = Tag.div()
    a_child = Tag.span()

    parent += a_child
    parent += a_child   # raise

def t2():
    parent = Tag.div()
    a_child = Tag.span()

    parent += [a_child,a_child] # raise

def t3():
    parent = Tag.div()
    a_child = Tag.span()

    parent += Tag.div(a_child)
    parent += Tag.div(a_child)  # raise


def t4():
    parent = Tag.div()
    a_child = Tag.span()

    parent <= Tag.div() <= a_child
    parent <= Tag.div() <= a_child  # raise

def t5():
    parent = Tag.div()
    a_child = Tag.span()

    parent.childs.append( a_child ) # since 'childs' is a tuple -> AttributeError
    parent.childs.append( a_child )

def test_strictmode_off():
    old=Tag.STRICT_MODE
    try:
        Tag.STRICT_MODE=False

        t0()
        t00()

        t1()
        t2()
        t3()
        t4()

        with pytest.raises(AttributeError): # AttributeError: 'tuple' object has no attribute 'append'
            t5()
    finally:
        Tag.STRICT_MODE=old

def test_strictmode_on():
    old=Tag.STRICT_MODE
    try:
        Tag.STRICT_MODE=True

        t0()

        with pytest.raises(HTagException):
            t00()

        with pytest.raises(HTagException):
            t1()

        with pytest.raises(HTagException):
            t2()

        with pytest.raises(HTagException):
            t3()

        with pytest.raises(HTagException):
            t4()

        with pytest.raises(AttributeError): # AttributeError: 'tuple' object has no attribute 'append'
            t5()

    finally:
        Tag.STRICT_MODE=old



if __name__=="__main__":
    # test_unparenting_clear()
    t0()