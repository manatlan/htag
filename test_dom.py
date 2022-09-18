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


#TODO: should not be possible !!!!
# def test_cant_add_many_times():
#     parent1 = Tag.div()
#     parent2 = Tag.div()

#     a_child = Tag.span()
#     parent1 += a_child

#     with pytest.raises(HTagException):
#         parent2 += a_child

if __name__=="__main__":
    test_unparenting_clear()