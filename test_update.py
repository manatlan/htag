#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
from dataclasses import replace
import pytest
import asyncio
import re

from htag import Tag,HTagException
from htag.render import Stater,HRenderer,fmtcaller

# Test new feature tag.update() with compatible hrenderer/runner (for htag > 0.10.0)

@pytest.mark.asyncio
async def test_update_default():
    class MyTag(Tag.div):
        def init(self):
            pass

    hr=HRenderer( MyTag, "//")

    tag=hr.tag
    assert not await tag.update()


@pytest.mark.asyncio
async def test_update_capable():
    class MyTag(Tag.div):
        def init(self):
            pass

    async def _sendactions(actions:dict) -> bool:
        assert "update" in actions
        assert "post" in actions
        ll=list(actions["update"].items())
        assert len(ll)==1
        id,content = ll[0]
        assert str(id) in content
        assert ">hello<" in content
        return True

    hr=HRenderer( MyTag, "//")
    hr.sendactions = _sendactions

    tag=hr.tag
    tag+="hello"
    tag.js="console.log(42)"    # add a js/post
    assert await tag.update()




if __name__=="__main__":
    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # asyncio.run( test_update_default() )
    asyncio.run( test_update_capable() )