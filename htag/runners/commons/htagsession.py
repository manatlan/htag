# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

import json
import sys
import typing
import uuid
import time

from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Literal
else:  # pragma: no cover
    from typing_extensions import Literal


class HtagSession:  # ASGI Middleware, for starlette
    """
    from htagsession import HtagSession

    app = Starlette(debug=True)
    app.add_middleware(HtagSession)
    """
    def __init__(
        self,
        app: ASGIApp,
        sessions: dict,
        session_cookie: str = "session",
        max_age: typing.Optional[int] = 0, #14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
    ) -> None:
        self.app = app
        self._sessions=sessions
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)

        if self.session_cookie in connection.cookies:
            htuid = connection.cookies[self.session_cookie]
            if htuid not in self._sessions:
                self._sessions[htuid]={}
        else:
            htuid=str(uuid.uuid4())
            self._sessions[htuid]={}

        scope["session"] = self._sessions.get(htuid,{"id":htuid})   # provide id session (htuid)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                # send it back, in all cases
                data = htuid
                headers = MutableHeaders(scope=message)
                header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                    session_cookie=self.session_cookie,
                    data=data,
                    path=self.path,
                    max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                    security_flags=self.security_flags,
                )
                headers.append("Set-Cookie", header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)

