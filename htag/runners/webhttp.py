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
"""

import uuid
import time
import asyncio
import logging

from starlette.applications import Starlette
from starlette.responses import HTMLResponse,JSONResponse,Response
from starlette.routing import Route
logger = logging.getLogger(__name__)

class WebHTTP(Starlette):
    """ Simple ASync Web Server (with starlette) with HTTP interactions with htag.
        can handle multiple instances & multiples Tag

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type, timeout=5*60):
        assert issubclass(tagClass,Tag)
        self.sessions={} # nb htag instances (htag x user)
        self.tagClass=tagClass
        self.timeout=timeout

        Starlette.__init__(self,debug=True, routes=[
            Route('/',   self.GET,   methods=["GET"]),
            Route('/{sesid}',   self.POST,  methods=["POST"]),
        ], on_startup=[self._purgeSessions])

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

    async def GET(self,request) -> HTMLResponse:
        print( "NB SES=",len(self.sessions) )
        return self.serve(request, self.tagClass )

    def serve(self,request, klass, init=None) -> HTMLResponse:
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

        hr = self.instanciate(htuid, klass, init )

        r = HTMLResponse( str(hr) )
        r.set_cookie("htuid",htuid,path="/")
        return r

    def instanciate(self, htuid, klass, init) -> HRenderer:
        """ get|create an instance of `klass` for user session `htuid`
        (get|save it into self.sessions)
        """
        sesid = f"{klass.__name__}|{htuid}"   # there can be only one instance of klass, at a time !

        if sesid in self.sessions and self.sessions[sesid]["renderer"].init == init:
            # same url (same klass/params), same htuid -> same instance
            hr=self.sessions[sesid]["renderer"]
        else:
            # url has changed ... recreate an instance
            js = """
                async function interact( o ) {
                    action( await (await window.fetch("/%s",{method:"POST", body:JSON.stringify(o)})).text() )
                }

                window.addEventListener('DOMContentLoaded', start );
            """ % sesid

            hr=HRenderer(klass, js, init=init ) # NO EXIT !!

        # update session info
        self.sessions[ sesid ] = dict(
            lastaccess=time.time(),
            renderer=hr,
        )

        return hr


    async def POST(self,request) -> Response:
        sesid=request.path_params.get('sesid',None)

        if sesid in self.sessions:
            hr = self.sessions[ sesid ]["renderer"]

            logger.info("INTERACT WITH SESSION %s (sessions:%s)",sesid,len(self.sessions))
            data=await request.json()
            actions = await hr.interact(data["id"],data["method"],data["args"],data["kargs"])
            return JSONResponse(actions)

        else:
            # session expired or bad call
            return HTMLResponse( "400 BAD REQUEST" , status_code=400 )



    def run(self, host="0.0.0.0", port=8000):   # wide, by default !!
        import uvicorn
        uvicorn.run(self, host=host, port=port)
