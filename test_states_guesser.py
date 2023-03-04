from htag import Tag
from htag.render import Stater

import pytest

@pytest.fixture(params=[1,2,3,4,5])
def env(request):
    A=Tag.A("a")
    B=Tag.B("b")
    C=Tag.C("c")
    D=Tag.D("d")

    A <= B <= C + D
    assert str(A)== "<A>a<B>b<C>c</C><D>d</D></B></A>"

    if request.param == 1:
        modmethod= lambda x: x<="mod"
    elif request.param == 2:
        modmethod= lambda x: x.__setitem__("class","mod")
    elif request.param == 3:
        modmethod= lambda x: x.clear()
    elif request.param == 4:
        modmethod= lambda x: x<=Tag.X("x")
    elif request.param == 5:
        modmethod= lambda x: x.__setitem__("class","mod") or x<="mod"

    return Stater(A),A,B,C,D,modmethod


def test_no_mod(env):
    s,A,B,C,D,mod = env

    assert s.guess()==[]


def test_mod_a_leaf(env):
    s,A,B,C,D,mod = env

    mod(C)
    assert s.guess()==[C]


def test_mod_the_two_leaf(env):
    s,A,B,C,D,mod = env

    mod(D)
    mod(C)
    assert s.guess()==[C,D]

def test_mod_the_two_leaf_in_other_order(env):
    s,A,B,C,D,mod = env

    mod(C)
    mod(D)
    assert s.guess()==[C,D]

def test_mod_a_leaf_and_its_parent(env):
    s,A,B,C,D,mod = env

    mod(D)
    mod(B)
    assert s.guess()==[B]   # just B (coz B include D)



def test_mod_the_root(env):
    s,A,B,C,D,mod = env

    mod(A)
    assert s.guess()==[A]


#########################
# same tests ^^but with placeholder in the middle
#########################


@pytest.fixture(params=[1,3,4])
def env_placeholder(request):
    A=Tag.A("a")
    B=Tag("b")
    C=Tag.C("c")
    D=Tag.D("d")

    A <= B <= C + D
    assert str(A)== "<A>ab<C>c</C><D>d</D></A>"

    if request.param == 1:
        modmethod= lambda x: x<="mod"
    elif request.param == 3:
        modmethod= lambda x: x.clear()
    elif request.param == 4:
        modmethod= lambda x: x<=Tag.X("x")

    return Stater(A),A,B,C,D,modmethod


def test_ph_no_mod(env_placeholder):
    s,A,B,C,D,mod = env_placeholder

    assert s.guess()==[]


def test_ph_mod_a_leaf(env_placeholder):
    s,A,B,C,D,mod = env_placeholder

    mod(C)
    assert s.guess()==[C]


def test_ph_mod_the_two_leaf(env_placeholder):
    s,A,B,C,D,mod = env_placeholder

    mod(D)
    mod(C)
    assert s.guess()==[C,D]

def test_ph_mod_the_two_leaf_in_other_order(env_placeholder):
    s,A,B,C,D,mod = env_placeholder

    mod(C)
    mod(D)
    assert s.guess()==[C,D]

def test_ph_mod_a_leaf_and_its_parent(env_placeholder):
    s,A,B,C,D,mod = env_placeholder

    mod(D)
    mod(B)
    # assert s.guess()==[B]   # just B (coz B include D)
    assert s.guess()==[A]   # just B (coz B include D)

def test_ph_mod_the_root(env_placeholder):
    s,A,B,C,D,mod = env_placeholder

    mod(A)
    assert s.guess()==[A]


if __name__=="__main__":
    pytest.main()
