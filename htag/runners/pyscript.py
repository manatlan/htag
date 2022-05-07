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
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        self.renderer=HRenderer(tagClass, "//")

    def run(self,window):
        window.interactions = self.interactions

        # put javascript in
        window.eval("""
window.interact=async function(o) {
     let actions = await window.interactions( JSON.stringify(o) );
     window.action( JSON.parse(actions) )
}

window.action = function( o ) {
    if(o.hasOwnProperty("update"))
        Object.keys(o["update"]).forEach(key => {
            document.getElementById( key ).outerHTML = o["update"][key];
        });
    if(o.hasOwnProperty("stream"))
        Object.keys(o["stream"]).forEach(key => {
            document.getElementById( key ).innerHTML += o["stream"][key];
        });

    if(o.hasOwnProperty("post")) eval( o["post"] );
    if(o.hasOwnProperty("next")) eval( o["next"] );
    if(o.hasOwnProperty("err"))  console.log( "ERROR", o["err"] );
}

window.start=function() {
    window.interact( {"id":0, "method":null, "args":null, "kargs":null} )
}
""")
        # install statics
        head = window.document.getElementsByTagName("head")[0]
        for s in self.renderer._statics:
            head.innerHTML+=str(s);

        # install the first object
        window.document.getElementsByTagName("body")[0].outerHTML=str(Tag.H.body( "Loading...", _id=0 ))

        # and start the process
        window.start()

    async def interactions(self, o):
        data=json.loads(o)
        actions = await self.renderer.interact( data["id"], data["method"], data["args"], data["kargs"] )
        return json.dumps(actions)
