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

""" REAL WEB http,
- .exit() has no effect ;-)
- can handle multiple client (with htuid cookie)
- can handle multiple "tag class", and brings query_params as "query_params:dict" when instanciate tag
- the session are purged automatically after timeout/5m of inactivity
- "http get query_params" are passed at Tag'init, if it accepts a query_params:dict param. (needed for https://htag.glitch.me)
"""

import uuid
import time
import asyncio
import logging

from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse,Response
from starlette.routing import Route
logger = logging.getLogger(__name__)

class WebHTTP:
    """ Simple ASync Web Server (with starlette) with HTTP interactions with htag.
        can handle multiple instances & multiples Tag
    """
    def __init__(self,*classes, timeout=5*60):
        assert len(classes)>0
        assert all( [issubclass(i,Tag) for i in classes] )
        self.sessions={}
        self.classes={i.__name__:i for i in classes}
        self.timeout=timeout

    async def _purgeSessions(self):

        async def purge():
            while True:
                now=time.time()
                for ses_id,ses_info in list(self.sessions.items()):
                    if now - ses_info["lastaccess"] > self.timeout:
                        logger.info("PURGE SESSION: %s (sessions:%s)", ses_id, len(self.sessions))
                        del self.sessions[ses_id]

                await asyncio.sleep(60) # check every 60s

        asyncio.ensure_future( purge() )


    def createHRenderer(self,tagClass,params):
        js = """
async function interact( o ) {
    action( await (await window.fetch("/%s/",{method:"POST", body:JSON.stringify(o)})).json() )
}

window.addEventListener('DOMContentLoaded', start );
""" % (tagClass.__name__)

        return HRenderer(tagClass, js , init = params) # NO EXIT !!

    def getsession(self,request,sessionid,klass):
        qp = dict(request.query_params)
        hr=None

        if sessionid in self.sessions:
            ses = self.sessions[ sessionid ]
            if request.method == "GET" and ses["qp"] != qp:
                # if we are at "CREATE TIME", we control query_params
                # not same construction -> destroy it (for recreate later)
                hr=None
                logger.info("FORGET SESSION %s (sessions:%s)",sessionid,len(self.sessions))
            else:
                ses["lastaccess"] = time.time()
                hr = ses["renderer"]
                logger.info("REUSE SESSION %s (sessions:%s)",sessionid,len(self.sessions))

        if hr is None:
            # need a new session
            params = ( (), dict(query_params = qp) )

            hr=self.createHRenderer(klass, params)
            self.sessions[ sessionid ] = dict( lastaccess=time.time(), renderer=hr, qp=qp )
            logger.info("CREATE SESSION %s for %s with qp=%s (sessions:%s)",sessionid,repr(hr.tag),qp,len(self.sessions))
        return hr


    async def GET(self,request) -> HTMLResponse:
        tagClass=request.path_params.get('tagClass',None)
        if tagClass is None:
            # by default, take the first one
            klass=list(self.classes.values())[0]
        else:
            # take the named one
            klass=self.classes.get(tagClass,None)

        if klass:
            htuid = request.cookies.get("htuid")

            if htuid:
                sessionid = klass.__name__+":"+htuid
            else:
                htuid = str(uuid.uuid4())
                sessionid = klass.__name__+":"+htuid

            hr = self.getsession(request,sessionid,klass)

            r=HTMLResponse( str(hr) )
            r.set_cookie("htuid",htuid,path="/")
            return r
        else:
            return HTMLResponse( "404 Not Found" , status_code=404 )

    async def POST(self,request) -> Response:
        tagClass=request.path_params.get('tagClass',None)
        klass=self.classes.get(tagClass,None)

        if klass and request.cookies.get('htuid'):
            htuid = request.cookies.get('htuid')
            sessionid = klass.__name__+":"+htuid
            hr = self.getsession(request,sessionid,klass)

            logger.info("INTERACT WITH SESSION %s (sessions:%s)",sessionid,len(self.sessions))
            data=await request.json()
            actions = await hr.interact(data["id"],data["method"],data["args"],data["kargs"])
            return JSONResponse(actions)
        else:
            return HTMLResponse( "404 Not Found" , status_code=404 )


    def __call__(self):
        """ create a uvicorn factory/asgi, to make it compatible with uvicorn
            from scratch.
        """
        app = Starlette(debug=True, routes=[
            Route('/',              self.GET,   methods=["GET"]),
            Route('/{tagClass}',    self.GET,   methods=["GET"]),
            Route('/{tagClass}/',   self.POST,  methods=["POST"]),
        ], on_startup=[self._purgeSessions])
        return app

    def run(self, host="0.0.0.0", port=8000):   # wide, by default !!
        import uvicorn
        uvicorn.run(self(), host=host, port=port)
