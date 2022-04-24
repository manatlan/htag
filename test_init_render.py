#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from typing import Type
import pytest

from htag import H,Tag,HTagException
from htag.tag import TagBase

anon=lambda t: str(t).replace( str(id(t)),"*" )


################################################################################################################
def test_simplified_init():
    class Toto(Tag.div): pass
    assert anon(Toto()) == '<div id="*"></div>'

    class Toto(Tag.div):
        def init(self,v):
            self.add(v)
    assert anon(Toto("hello")) == '<div id="*">hello</div>'
    assert anon(Toto("hello",_data_text='my')) == '<div data-text="my" id="*">hello</div>'

    with pytest.raises(TypeError): # can't auto assign instance attribut with own simplified init()
        Toto(js="tag.focus()")

    class Toto(Tag.div):
        def init(self,v,vv=42):
            self.add(v)
            self.add(vv)
    assert anon(Toto("hello")) == '<div id="*">hello42</div>'
    assert anon(Toto("hello",43)) == '<div id="*">hello43</div>'
    assert anon(Toto("hello",vv=44)) == '<div id="*">hello44</div>'

    assert anon(Toto("hello",_class='my')) == '<div class="my" id="*">hello42</div>'
    assert anon(Toto("hello",_class='my',vv=45)) == '<div class="my" id="*">hello45</div>'

def test_own_render():
    class Toto(Tag.div):
        def render(self):
            self <= "own"
    assert anon(Toto("hello")) == '<div id="*">own</div>'

    class Toto(Tag.div):
        def init(self,nb):
            self.nb=nb
        def render(self):
            self <= "*" * self.nb
    t=Toto(4)
    assert anon(t) == '<div id="*">****</div>'
    t.nb=8
    assert anon(t) == '<div id="*">********</div>'



def test_weird_with_real_constructor():
    class Toto(Tag.div):
        def __init__(self):
            super().__init__()
    assert anon(Toto()) == '<div id="*"></div>'

    class Toto(Tag.div):
        def __init__(self):
            super().__init__(1)
    assert anon(Toto()) == '<div id="*">1</div>'

    class Toto(Tag.div):
        def __init__(self):
            super().__init__(1,2)

    with pytest.raises(TypeError):
        Toto()

    class Toto(Tag.div):
        def __init__(self):
            super().__init__(1,js="tag.focus()")

    t=Toto()
    assert anon(t) == '<div id="*">1</div>'
    assert t.js == "tag.focus()"


if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)

    test_simplified_init()
    test_own_render()
    test_weird_with_real_constructor()
