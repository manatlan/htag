from htag import Tag
import pytest


#####################################################################################
# test base
#####################################################################################

def test_basic_creation():  # auto init (property/html_attributes) in all cases
    # test base constructor
    t=Tag.div("hello",param1=12,_param2=13)
    assert t.param1 == 12
    assert t["param2"] == 13

class MyDiv(Tag.div):
    pass

def test_basic_inherited_creation(): # auto init (property/html_attributes) in all cases
    # test Tag simple inherits (no constructor)
    t=MyDiv("hello",param1=12,_param2=13)
    assert t.param1 == 12
    assert t["param2"] == 13






#####################################################################################
# test Tag constructor with real/python __init__() method
#####################################################################################

#############################################
## with real __init__() constructor
#############################################

class MyRDivOpen(Tag.div):                  # accept auto set property/html_attributes
    def __init__(self,content,**a):
        Tag.div.__init__(self,content,**a)

class MyRDivClosed(Tag.div):                # DONT't accept auto set property/html_attributes
    def __init__(self,content):
        Tag.div.__init__(self,content)


def test_real_inherited_creation():
    # test Tag inherited with __init__() constructor
    t=MyRDivOpen("hi",param1=12,_param2=13)
    assert t.param1 == 12
    assert t["param2"] == 13

    t=MyRDivOpen(content="hi",param1=12,_param2=13)
    assert t.param1 == 12
    assert t["param2"] == 13

    with pytest.raises(TypeError):
        MyRDivClosed("hi",param1=12)

    with pytest.raises(TypeError):
        MyRDivClosed("hi",_param2=13)





#####################################################################################
# test Tag constructor with simplified init() method
#####################################################################################


#############################################
## with simplified init() constructor
#############################################

class MyDivOpen(Tag.div):          # accept auto set property/html_attributes
    def init(self,content,**a):    # <- **a
        self <= content

class MyDivClosed(Tag.div):        # DONT't accept auto set property/html_attributes
    def init(self,content):        # no **a !
        self <= content

def test_simplified_inherited_creation():

    # test Tag inherited with init() constructor
    t=MyDivOpen("hi",param1=12,_param2=13)
    assert t.param1 == 12
    assert t["param2"] == 13

    t=MyDivOpen(content="hi",param1=12,_param2=13)
    assert t.param1 == 12
    assert t["param2"] == 13

    with pytest.raises(TypeError):
        MyDivClosed("hi",param1=12)

    with pytest.raises(TypeError):
        MyDivClosed("hi",_param2=13)

