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

import json

class PyScript:

    def __init__(self,*classes):
        assert len(classes)>0
        assert all( [issubclass(i,Tag) for i in classes] )

        self.classes={}
        for i in classes:
            tagClass = i.__name__
            js = """
interact=async function(o) {
     let actions = await window.interactions( "%s", JSON.stringify(o) );
     action( JSON.parse(actions) )
}

""" % tagClass
            self.classes[tagClass] = HRenderer(i, js)

        self._window = None


    def run(self,window): # window: "pyscript js.window"
        window.interactions = self.interactions
        assert window.document.head, "No <head> in <html>"
        assert window.document.body, "No <body> in <html>"

        hash = window.document.location.hash
        if hash in ["#","",None]:
            current = list(self.classes.values())[0]
        else:
            current = self.classes.get(hash[1:],None)
            assert current, "Unknown htag tag '%s'" % hash[1:]


        # install statics in headers
        window.document.head.innerHTML=""
        for s in current._statics:
            tag=window.document.createElement(s.tag)
            tag.innerHTML = "".join([str(i) for i in s.childs if i is not None])
            for key,value in s.attrs.items():
                setattr(tag, key, value)
            window.document.head.appendChild(tag)

        # install the first object in body
        window.document.body.outerHTML=str(Tag.H.body( _id=0 ))

        # and start the process
        window.start()

        # save it, for hashchange
        if self._window is None :
            # install the hashchange event
            # (which can only work, after the run())
            import pyodide
            def _rerun_(event):
                if self._window: self.run( self._window )
            window.addEventListener("hashchange", pyodide.create_proxy(_rerun_) )

        self._window = window


    async def interactions(self, tagClass, o):
        current = self.classes[tagClass]

        data=json.loads(o)
        actions = await current.interact( data["id"], data["method"], data["args"], data["kargs"] )
        return json.dumps(actions)
