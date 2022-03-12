# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/thag
# #############################################################################

from .. import Tag
from ..render import HRenderer

import asyncio
import socket
import webbrowser,os,json

class BrowserHTTP:
    """ Simple ASync Web Server with HTTP interactions with Thag. (only stdlib!)
        Open the rendering in a browser tab.

        Should not be used AS IS in a real app ...
        But it's the perfect runner, to test/debug, coz interactions are easier !
    """

    def __init__(self,tag:Tag):
        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).json() )
}

window.addEventListener('DOMContentLoaded', start );
"""

        self.renderer=HRenderer(tag, js, lambda: os._exit(0))

    def run(self):
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
            req = await loop.sock_recv(conn, 8192)
            if req.startswith(b"GET / HTTP"):
                resp = make_header()
                resp += str(self.renderer)
            elif req.startswith(b"POST / HTTP"):
                _,content = req.split(b"\r\n\r\n")
                data = json.loads(content.decode())
                dico = await self.renderer.interact(data["id"],data["method"],data["args"],data["kargs"] )
                resp = make_header("application/json")
                resp += json.dumps(dico)
            else:
                resp = "HTTP/1.1 404 NOT FOUND\r\n"
            await loop.sock_sendall(conn, resp.encode())
            conn.close()

        async def server(sock, loop):
            while True:
                conn, addr = await loop.sock_accept(sock)
                loop.create_task(handler(conn))

        host = '127.0.0.1'
        port = 8000
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setblocking(False)
            s.bind((host, port))
            s.listen(10)

            loop = asyncio.get_event_loop()
            try:
                webbrowser.open_new_tab(f"http://{host}:{port}")
                loop.run_until_complete(server(s, loop))
            except KeyboardInterrupt:
                pass
            finally:
                loop.close()
