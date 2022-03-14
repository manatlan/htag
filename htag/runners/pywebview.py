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


import asyncio,os
try:
    import webview
except ImportError:
    import sys
    print("You should install 'pywebview' for this htag runner")
    sys.exit(-1)


"""
LIMITATION :

til pywebview doen't support async jsapi ...(https://github.com/r0x0r/pywebview/issues/867)
it can't work for "async generator" with the asyncio.run() trick (line 50)

"""
#window.addEventListener('pywebviewready', async function() { await window.pywebview.api.start() });

class PyWebWiew:
    """ Open the rendering in a pywebview instance
        Interactions with builtin pywebview.api ;-)
    """
    def __init__(self,tag:Tag):
        js = """
async function interact( o ) {
    action( await pywebview.api.interact( o["id"], o["method"], o["args"], o["kargs"] ) );
}

window.addEventListener('pywebviewready', start );
"""

        self.renderer=HRenderer(tag, js, lambda: os._exit(0))

    def run(self):
        class Api:
            def interact(this,tagid,method,args,kargs):
                return asyncio.run(self.renderer.interact(tagid,method,args,kargs))

        window = webview.create_window(self.renderer.title, html=str(self.renderer), js_api=Api(),text_select=True)
        webview.start(debug=False)

    def exit(self,rc=0):
        os._exit(rc)
