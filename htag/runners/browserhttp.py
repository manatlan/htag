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

import asyncio
import socket
import webbrowser,os,json
import urllib.parse

class BrowserHTTP:
    """ Simple ASync Web Server with HTTP interactions with HTag. (only stdlib!)
        Open the rendering in a browser tab.

        Should not be used AS IS in a real app ...
        But it's the perfect runner, to test/debug, coz interactions are easier !
    """

    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        self.hrenderer=None
        self.tagClass=tagClass

    def instanciate(self,url:str):
        init = commons.url2ak(url)
        if self.hrenderer and self.hrenderer.init == init:
            return self.hrenderer

        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).text() )
}

window.addEventListener('DOMContentLoaded', start );
"""
        return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init)

    def run(self, host="127.0.0.1", port=8000, openBrowser=True ):   # localhost, by default !!
        """
        ASyncio http server with stdlib ;-)
        Inspired from https://www.pythonsheets.com/notes/python-asyncio.html
        """

        def make_header(type="text/html"):
            header  =  "HTTP/1.1 200 OK\r\n"
            header += f"Content-Type: {type}\r\n"
            header +=  "\r\n"
            return header

        async def handler(conn):

            CHUNK_LIMIT=256 # must be minimal
            req = b''
            while True:
                chunk = await loop.sock_recv(conn, CHUNK_LIMIT)
                if chunk:
                    req += chunk
                    if len(chunk) < CHUNK_LIMIT:
                        break
                else:
                    break


            try:
                # if req.startswith(b"GET / HTTP"):
                if req.startswith(b"GET /"):
                    url=req.decode()[4:].split(" HTTP")[0]

                    info = urllib.parse.urlsplit(url)
                    if info.path=="/":
                        self.hrenderer = self.instanciate(url)
                        resp = make_header()
                        resp += str(self.hrenderer)
                    else:
                        resp = "HTTP/1.1 404 NOT FOUND\r\n"
                elif req.startswith(b"POST / HTTP"):
                    _,content = req.split(b"\r\n\r\n")
                    data = json.loads(content.decode())
                    dico = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event") )
                    resp = make_header("application/json")
                    resp += json.dumps(dico)
                else:
                    resp = "HTTP/1.1 404 NOT FOUND\r\n"
            except Exception as e:
                print("SERVER ERROR:",e)
                resp = "HTTP/1.1 500 SERVER ERROR\r\n"

            await loop.sock_sendall(conn, resp.encode())
            conn.close()

        async def server(sock, loop):
            while True:
                conn, addr = await loop.sock_accept(sock)
                loop.create_task(handler(conn))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setblocking(False)
            s.bind((host, port))
            s.listen(10)

            loop = asyncio.get_event_loop()
            try:
                if openBrowser:
                    webbrowser.open_new_tab(f"http://{host}:{port}")
                loop.run_until_complete(server(s, loop))
            except KeyboardInterrupt:
                pass
            finally:
                loop.close()
