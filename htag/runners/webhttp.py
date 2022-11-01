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



""" REAL WEB http,
- .exit() has no effect ;-)
- can handle multiple client (with htuid cookie)
- can handle multiple "tag class", and brings query_params as "query_params:dict" when instanciate tag
- the session are purged automatically after timeout/5m of inactivity
- "http get query_params" are passed at Tag'init, if it accepts a query_params:dict param. (needed for https://htag.glitch.me)
- the main root is setable with path parameter (default: "/")
- add renew (bool) parametter on .serve() (and instanciate), to force renewal in all cases.
"""

import uuid
import time
import asyncio
import logging

from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse,Response
from starlette.routing import Route
logger = logging.getLogger(__name__)

QN = lambda klass: (klass.__module__+"."+klass.__qualname__).replace("__main__.","")

class WebHTTP(Starlette):
    """ Simple ASync Web Server (with starlette) with HTTP interactions with htag.
        can handle multiple instances & multiples Tag

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type=None, timeout=5*60):
        if tagClass: assert issubclass(tagClass,Tag)
        self.sessions=common.Sessions()
        self.tagClass=tagClass
        self.timeout=timeout

        routes=[ Route('/{sesid}',   self.POST,  methods=["POST"]) ]
        if tagClass:
            routes.append( Route("/",   self.GET,   methods=["GET"]) )

        Starlette.__init__(self,debug=True, routes=routes, on_startup=[self._purgeSessions])

    async def _purgeSessions(self):

        async def purge():
            while True:
                self.sessions.purge( self.timeout )
                await asyncio.sleep(60) # check every 60s

        asyncio.ensure_future( purge() )

    async def GET(self,request) -> HTMLResponse:
        return self.serve(request, self.tagClass )

    def serve(self,request, klass, init=None, renew=False) -> HTMLResponse:
        """ Serve for the `request`, an instance of the class 'klass'
        initialized with `init` (tuple (*args,**kargs))
        if init is None : takes them from request.url ;-)

        return an htmlresponse (htag init page to start all)
        """
        htuid = request.cookies.get('htuid') or str(uuid.uuid4())

        if init is None:
            # no init params
            # so we take thoses from the url
            init = common.url2ak( str(request.url) )
        else:
            assert type(init)==tuple
            assert type(init[0])==tuple
            assert type(init[1])==dict

        hr = self.instanciate(htuid, klass, init , renew)
        
        r = HTMLResponse( str(hr) )
        r.set_cookie("htuid",htuid,path="/")
        return r

    def instanciate(self, htuid, klass, init, renew) -> HRenderer:
        """ get|create an instance of `klass` for user session `htuid`
        (get|save it into self.sessions)
        """
        sesid = f"{QN(klass)}|{htuid}"   # there can be only one instance of klass, at a time !

        logger.info("intanciate : renew=%s",renew)
        hr=self.sessions.get_hr( sesid )
        if renew==False and hr and hr.init == init:
            # same url (same klass/params), same htuid -> same instance
            logger.info("intanciate : Reuse Renderer %s for %s",QN(klass),sesid)
        else:
            # url has changed ... recreate an instance
            logger.info("intanciate : Create Renderer %s for %s",QN(klass),sesid)
            js = """
                async function interact( o ) {
                    action( await (await window.fetch("/%s",{method:"POST", body:JSON.stringify(o)})).text() )
                }

                window.addEventListener('DOMContentLoaded', start );
            """ % sesid
            
            # create a session property on the future main tag instance
            klass.session = self.sessions.get_ses(htuid)["session"]
            
            hr=HRenderer(klass, js, init=init ) # NO EXIT !!


        # update session info
        self.sessions.set_hr( sesid, hr)

        return hr


    async def POST(self,request) -> Response:
        sesid=request.path_params.get('sesid',None)

        hr=self.sessions.get_hr(sesid)
        if hr:
            logger.info("INTERACT WITH SESSION %s",sesid)
            data=await request.json()
            actions = await hr.interact(data["id"],data["method"],data["args"],data["kargs"],data["event"])
            return JSONResponse(actions)
        else:
            # session expired or bad call
            return HTMLResponse( "400 BAD REQUEST" , status_code=400 )


    def run(self, host="0.0.0.0", port=8000):   # wide, by default !!
        import uvicorn
        uvicorn.run(self, host=host, port=port)
