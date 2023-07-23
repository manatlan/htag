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
from . import commons

import json

class PyScript:

    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)
        self.tagClass=tagClass

    def run(self,window): # window: "pyscript js.window"
        self.window=window

        js = """
interact=async function(o) {
 action( await window.interactions( JSON.stringify(o) ) );
}

function pyscript_starter() {
    if(document.querySelector("*[needToLoadBeforeStart]"))
        window.setTimeout( pyscript_starter, 100 )
    else
        window.start()
}
"""
        self.hr = HRenderer(self.tagClass, js, init=commons.url2ak( window.document.location.href ))
        self.hr.sendactions=self.updateactions

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
                    if key in ["src","href"]:
                        tag.setAttribute("needToLoadBeforeStart", True)
                        tag.onload = lambda o: o.target.removeAttribute("needToLoadBeforeStart")

                window.document.head.appendChild(tag)

        # install the first object in body
        window.document.body.outerHTML=str(self.hr)

        # and start the process
        window.pyscript_starter() # will run window.start, when dom ready

    async def interactions(self, o):
        data=json.loads(o)
        actions = await self.hr.interact( data["id"], data["method"], data["args"], data["kargs"], data.get("event") )
        return json.dumps(actions)

    async def updateactions(self, actions:dict):
        self.window.action( json.dumps(actions) )   # send action as json (not a js(py) object) ;-(