# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

from .. import Tag
from ..render import HRenderer
from . import common

import json

class PyScript:

    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)
        self.tagClass=tagClass

    def run(self,window): # window: "pyscript js.window"

        js = """
interact=async function(o) {
 action( await window.interactions( JSON.stringify(o) ) );
}"""
        self.hr = HRenderer(self.tagClass, js, init=common.url2ak( window.document.location.href ))

        window.interactions = self.interactions
        assert window.document.head, "No <head> in <html>"
        assert window.document.body, "No <body> in <html>"

        # install statics in headers
        window.document.head.innerHTML=""
        for s in self.hr._statics:
            if isinstance(s,Tag):
                tag=window.document.createElement(s.tag)
                tag.innerHTML = "".join([str(i) for i in s.childs if i is not None])
                for key,value in s.attrs.items():
                    setattr(tag, key, value)
                window.document.head.appendChild(tag)

        # install the first object in body
        window.document.body.outerHTML=str(self.hr)

        # and start the process
        window.start()

    async def interactions(self, o):
        data=json.loads(o)
        actions = await self.hr.interact( data["id"], data["method"], data["args"], data["kargs"], data.get("event") )
        return json.dumps(actions)
