# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2024 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

# heavily inspired from https://github.com/dpallot/asyncws (MIT licensed)
# "dpallot"

import sys
import asyncio
import base64
import hashlib
import codecs
import struct
import random
import urllib.parse
from io import BytesIO
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler

    
class ProtocolError(Exception):
    pass

class ClosedException(Exception):
    
    status = None
    reason = None
    
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason
    
    def __str__(self):
        return self.reason



_REQUEST = (
    'GET %(path)s HTTP/1.1\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Host: %(host_port)s\r\n'
    'Origin: file://\r\n'
    'Sec-WebSocket-Key: %(key)s\r\n'
    'Sec-WebSocket-Version: 13\r\n\r\n'
)

_RESPONSE = (
    'HTTP/1.1 101 Switching Protocols\r\n'
    'Upgrade: websocket\r\n'
    'Connection: Upgrade\r\n'
    'Sec-WebSocket-Accept: %(accept_string)s\r\n\r\n'
)

_GUID_STRING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

_STREAM = 0x0
_TEXT = 0x1
_BINARY = 0x2
_CLOSE = 0x8
_PING = 0x9
_PONG = 0xA

_VALID_STATUS_CODES = [1000, 1001, 1002, 1003, 1007, 1008, 1009, 1010, 1011, 3000, 3999, 4000, 4999]

class FakeSocket():
    def __init__(self, response_str):
        self._file = BytesIO(response_str)

    def makefile(self, *args, **kwargs):
        return self._file


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request):
        self.rfile = BytesIO(request)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    @property
    def method(self):
        return self.command

class Websocket:
    """
    Class that wraps the websocket protocol.

    :param writer: Access to ``get_extra_info()``. See `StreamWriter. \
        <https://docs.python.org/3.4/library/asyncio-stream.html#asyncio.StreamWriter>`_
    :param request: HTTP request that arrives at the server during handshaking. \
        See `BaseHTTPRequestHandler. \
        <https://docs.python.org/3.4/library/http.server.html#http.server.BaseHTTPRequestHandler>`_ \
        Set to ``None`` if it's a client websocket.
    :param response: HTTP response that arrives at the client after handshaking is complete. \
        See `HTTPResponse. <https://docs.python.org/3.4/library/http.client.html#http.client.HTTPResponse>`_ \
        Set to ``None`` if it's a server websocket.
    """
    def __init__(self, reader, writer):
        self.writer = writer
        self._reader = reader
        self._queue = asyncio.Queue()
        self._recv_task = None
        self.response = None
        self.request = None
        self._closed = False
        self._mask = False
        self.status = 1000
        self.reason = ''


    def destroy(self):
        self.writer.close()


    async def wait_closed(self):
        if self._recv_task:
            self._recv_task.cancel()
            await self._recv_task


    async def close(self, status=1000, reason=''):
        """
        Start the close handhake by sending a close frame to the websocket endpoint. \
            Once the endpoint responds with a corresponding close the underlying transport is closed.

        To force close the websocket without going through the close handshake call ``self.writer.close()``
        which will immediately tear down the underlying transport.

        :param status: See `Status Codes. <https://tools.ietf.org/html/rfc6455#section-7.4>`_
        :param reason: Why the websocket is being closed.
        :raises Exception: When there is an error sending data to the endpoint.
        """
        if self._closed is False:
            self._closed = True
            await send_close_frame(self.writer, status, reason, self._mask)


    
    async def send(self, data, flush=False):
        """
        Send a data frame to websocket endpoint.

        :param data: If data is of type ``str`` then the data is sent as a text frame.
                     If data is of type ``byte`` then the data is sent as a binary frame.
        :param flush: When set to ``True`` then the send buffer is flushed immediately.
        :raises Exception: When there is an error sending data to the endpoint only if flush is set to ``True``.
        """
        payload = data
        opcode = _BINARY
        if isinstance(data, str):
            opcode = _TEXT
            payload = data.encode('utf-8')

        await send_frame(self.writer, False, opcode, payload, self._mask, flush)


    async def send_fragment_start(self, data, flush=False):
        payload = data
        opcode = _BINARY
        if isinstance(data, str):
            opcode = _TEXT
            payload = data.encode('utf-8')

        await send_frame(self.writer, True, opcode, payload, self._mask, flush)


    async def send_fragment(self, data, flush=False):
        payload = data
        if isinstance(data, str):
            payload = data.encode('utf-8')

        await send_frame(self.writer, True, _STREAM, payload, self._mask, flush)


    async def send_fragment_end(self, data, flush=False):
        payload = data
        if isinstance(data, str):
            payload = data.encode('utf-8')

        await send_frame(self.writer, False, _STREAM, payload, self._mask, flush)


    async def ping(self, data, flush=False):
        payload = data
        if isinstance(data, str):
            payload = data.encode('utf-8')

        await send_frame(self.writer, False, _PING, payload, self._mask, flush)


    async def recv(self):
        """
        Receive websocket frame from endpoint.

        This coroutine will block until a complete frame is ready.

        :return: Websocket text or data frame on success. \
            Returns ``None`` if the connection is closed or there is an error.
        """

        if self._closed is True:
            return None

        item = await self._queue.get()
        self._queue.task_done()
        return item


async def recv_entire_frame(ws, **kwds):
    max_payload = kwds.get('max_payload', 33554432)
    try:
        _frag_start = False
        _frag_type = _BINARY
        _frag_buffer = None
        _frag_decoder = codecs.getincrementaldecoder('utf-8')()

        while True:
            fin, opcode, length, frame = await recv_frame(ws._reader, max_payload)
            if opcode == _CLOSE:
                status = 1000
                reason = b''
                length = len(frame)

                if length == 0:
                    pass
                elif length >= 2:
                    status = struct.unpack_from('!H', frame[:2])[0]
                    reason = frame[2:]

                    if status not in _VALID_STATUS_CODES:
                        status = 1002

                    if len(reason) > 0:
                        try:
                            reason = reason.decode('utf-8')
                        except:
                            status = 1002
                else:
                    status = 1002

                await ws.close(status, reason)
                raise ClosedException(status, reason)

            if fin == 0:
                # fragmentation start
                if opcode != _STREAM:
                    if opcode == _PING or opcode == _PONG or opcode == _CLOSE:
                        raise ClosedException(1002, 'control messages can not be fragmented')

                    _frag_type = opcode
                    _frag_start = True
                    _frag_decoder.reset()

                    if _frag_type == _TEXT:
                        _frag_buffer = []
                        utf_str = _frag_decoder.decode(frame, final=False)
                        if utf_str:
                            _frag_buffer.append(utf_str)
                    else:
                        _frag_buffer = bytearray()
                        _frag_buffer.extend(frame)

                    if len(_frag_buffer) > max_payload:
                        raise ClosedException(1009, 'payload too large')
                else:
                    # got a fragment packet without a start
                    if _frag_start is False:
                        raise ClosedException(1002, 'fragmentation protocol error')

                    if _frag_type == _TEXT:
                        utf_str = _frag_decoder.decode(frame, final=False)
                        if utf_str:
                            _frag_buffer.append(utf_str)
                    else:
                        _frag_buffer.extend(frame)

                    if len(_frag_buffer) > max_payload:
                        raise ClosedException(1009, 'payload too large')
            else:

                if opcode == _STREAM:
                    if _frag_start is False:
                        raise ClosedException(1002, 'fragmentation protocol error')

                    if _frag_type == _TEXT:
                        utf_str = _frag_decoder.decode(frame, final=True)
                        _frag_buffer.append(utf_str)
                        _frag_buffer = ''.join(_frag_buffer)
                    else:
                        _frag_buffer.extend(frame)
                        _frag_buffer = bytes(_frag_buffer)

                    if len(_frag_buffer) > max_payload:
                        raise ClosedException(1009, 'payload too large')

                    ws._queue.put_nowait(_frag_buffer)

                    _frag_start = False
                    _frag_type = _BINARY
                    _frag_buffer = None
                    _frag_decoder.reset()

                elif opcode == _PING:
                    await send_frame(ws.writer, False, _PONG, frame)

                elif opcode == _PONG:
                    continue

                else:
                    if _frag_start is True:
                        raise ClosedException(1002, 'fragmentation protocol error')

                    if opcode == _TEXT:
                        try:
                            frame = frame.decode('utf-8')
                        except Exception as exp:
                            raise ClosedException(1002, 'invalid utf-8 payload')

                    ws._queue.put_nowait(frame)

                    _frag_start = False
                    _frag_type = _BINARY
                    _frag_buffer = None
                    _frag_decoder.reset()

    except BaseException as exp:
        ws.writer.close()
        status = 1002
        if isinstance(exp, ClosedException):
            status = exp.status
            reason = exp.reason
        else:
            reason = str(exp)
        ws.status = status
        ws.reason = reason
        ws._closed = True
        ws._queue.put_nowait(None)


async def connect(wsurl, **kwds):
    """
    Connect to a websocket server. Connect will automatically carry out a websocket handshake.

    :param wsurl: Websocket uri. See `RFC6455 URIs. <https://tools.ietf.org/html/rfc6455#section-3>`_
    :param kwds: See `open_connection. \
        <https://docs.python.org/3.4/library/asyncio-stream.html#asyncio.open_connection>`_
    :return: :class:`Websocket` object on success.
    :raises Exception: When there is an error during connection or handshake.
    """
    writer = None
    try:
        url = urllib.parse.urlparse(wsurl)
        port = 80
        if url.port:
            port = url.port
        if url.scheme.startswith('wss://'):
            if not url.port:
                port = 443

        reader, writer = await asyncio.open_connection(host=url.hostname, port=port, **kwds)
        response = await handshake_with_server(reader, writer, url, **kwds)
        websocket = Websocket(reader, writer)
        websocket._mask = True
        websocket.reponse = response
        websocket._recv_task = asyncio.get_event_loop().create_task(
            recv_entire_frame(websocket, **kwds))
        return websocket
    except BaseException as exp:
        if writer:
            writer.close()
        raise exp


class WSServer(object):

    def __init__(self):
        self._server = None
        self._tasks = {}

    def add_task(self, task, value):
        self._tasks[task] = value

    def remove_task(self, task):
        del self._tasks[task]

    @property
    def server(self):
        return self._server

    @server.setter
    def server(self, value):
        self._server = value

    def close(self):
        self._server.close()

        for task in self._tasks:
            task.cancel()

    async def wait_closed(self):
        await self._server.wait_closed()

        tasks = self._tasks.keys()
        if len(tasks) > 0:
            await asyncio.wait(tasks)


async def start_server(funchttp,funcws, host=None, port=None, **kwds):
    """
    Start a websocket server, with a callback for each client connected.

    :param funcws: Called with a :class:`Websocket` parameter when a client connects and handshake is successful.
    :param kwds: See `start_server <https://docs.python.org/3.4/library/asyncio-stream.html#asyncio.start_server>`_
    :return: The return value is the same as `start_server \
    <https://docs.python.org/3.4/library/asyncio-stream.html#asyncio.start_server>`_
    """
    ws_server = WSServer()
    server = await asyncio.start_server(
        lambda r, w: handle_server_websocket(r, w, ws_server, funchttp, funcws), host, port, **kwds)
    ws_server.server = server
    return ws_server


async def handle_server_websocket(reader, writer, server, funchttp, func, **kwds):
    try:
        websocket = Websocket(reader, writer)
        handshake_timeout = kwds.get('handshake_timeout', 12)
        try:
            request = await asyncio.wait_for(
                handshake_with_client(reader, writer,funchttp, **kwds), timeout=handshake_timeout)
            websocket.request = request
        except BaseException as e:
            websocket._closed = True

        def task_done(task):
            server.remove_task(task)

        recv_task = asyncio.ensure_future(recv_entire_frame(websocket, **kwds))
        server.add_task(recv_task, websocket)
        recv_task.add_done_callback(task_done)

        func_task = asyncio.ensure_future(func(websocket))
        server.add_task(func_task, websocket)
        func_task.add_done_callback(task_done)

        await func_task

    except BaseException:
        pass
    finally:
        writer.close()


async def handshake_with_server(reader, writer, parsed_url, **kwds):
    max_header = kwds.get('max_header', 65536)
    try:
        rand = bytes(random.getrandbits(8) for _ in range(16))
        key = base64.b64encode(rand).decode()

        values = ''
        if parsed_url.query:
            values = '?{0}'.format(parsed_url.query)

        handshake = _REQUEST % {'path': parsed_url.path + values, 'host_port': parsed_url.netloc, 'key': key}

        writer.write(handshake.encode('utf-8'))
        await writer.drain()

        header_buffer = bytearray()
        while True:
            header = await reader.readline()
            if len(header) == 0:
                raise ProtocolError('no data from endpoint')

            header_buffer.extend(header)
            if len(header_buffer) > max_header:
                raise ProtocolError('header too large')

            if header in b'\r\n':
                break

        response = HTTPResponse(FakeSocket(header_buffer))
        response.begin()

        accept_key = response.getheader('sec-websocket-accept')
        if key is None:
            raise ProtocolError('Sec-WebSocket-Accept does not exist')

        digested_key = base64.b64encode(hashlib.sha1((key + _GUID_STRING).encode('utf-8')).digest())
        if accept_key.encode() != digested_key:
            raise ProtocolError('Sec-WebSocket-Accept key does not match')

        return response

    except asyncio.CancelledError:
        writer.close()


async def handshake_with_client(reader, writer, funchttp, **kwds):
    max_header = kwds.get('max_header', 65536)
    try:
        header_buffer = bytearray()
        while True:
            header = await reader.readline()
            
            
            if len(header) == 0:
                raise ClosedException(1002, 'no data from endpoint')

            header_buffer.extend(header)
            if len(header_buffer) > max_header:
                raise ClosedException(1009, 'header too large')

            if header in b'\r\n':
                break

        request = HTTPRequest(header_buffer)
        ############################################################################################### insert me
        if request.headers.get("connection","").lower() == "keep-alive":    # not 'upgrade'
            if request.method in ["POST","PUT","DELETE"]:
                request.body = await reader.read(10_000_000)
            else:
                request.body = None
            response:HTTPResponse = await funchttp( request )
            writer.write( response.toHTTPResponse() )
            return request
        ###############################################################################################
        key = request.headers.get('sec-websocket-key', None)
        if key is None:
            raise ClosedException(1002, 'Sec-WebSocket-Key does not exist')

        digest = base64.b64encode(hashlib.sha1((key + _GUID_STRING).encode('utf-8')).digest())
        handshake = _RESPONSE % {'accept_string': digest.decode('utf-8')}
        writer.write(handshake.encode('utf-8'))
        await writer.drain()
        return request

    except asyncio.CancelledError as excp:
        response = 'HTTP/1.1 400 Bad Request\r\n\r\n{0}'.format(str(excp))
        writer.write(response.encode('utf-8'))
        writer.close()

    except BaseException as exp:
        response = 'HTTP/1.1 400 Bad Request\r\n\r\n{0}'.format(str(exp))
        writer.write(response.encode('utf-8'))
        writer.close()

        if not isinstance(exp, ClosedException):
            raise ClosedException(1002, str(exp))

        raise exp


async def send_close_frame(writer, status=1000, reason='', mask=False):
    close_msg = bytearray()
    close_msg.extend(struct.pack('!H', status))
    if isinstance(reason, str):
        close_msg.extend(reason.encode('utf-8'))
    else:
        close_msg.extend(reason)

    await send_frame(writer, False, _CLOSE, close_msg, mask, True)


native_byteorder = sys.byteorder
def mask_data(mask, data):
    datalen = len(data)
    data = int.from_bytes(data, native_byteorder)
    mask = int.from_bytes(mask * (datalen // 4) + mask[: datalen % 4], native_byteorder)
    return (data ^ mask).to_bytes(datalen, native_byteorder)



async def send_frame(writer, fin, opcode, data, mask=False, flush=False):
    header = bytearray()
    b1 = 0
    b2 = 0

    if fin is False:
        b1 |= 0x80

    b1 |= opcode
    header.append(b1)

    if mask:
        b2 |= 0x80

    length = len(data)
    if length <= 125:
        b2 |= length
        header.append(b2)
    elif 126 <= length <= 65535:
        b2 |= 126
        header.append(b2)
        header.extend(struct.pack('!H', length))
    else:
        b2 |= 127
        header.append(b2)
        header.extend(struct.pack('!Q', length))

    writer.write(header)

    if mask:
        mask_bits = struct.pack('!I', random.getrandbits(32))
        writer.write(mask_bits)
        data = mask_data(mask_bits, data)

    if length > 0:
        writer.write(data)

    if flush:
        await writer.drain()


async def recv_frame(reader, max_payload):

    h1, h2 = await reader.readexactly(2)

    fin = h1 & 0x80
    rsv = h1 & 0x70
    opcode = h1 & 0x0F
    mask = h2 & 0x80
    length = h2 & 0x7F

    # rsv must be 0 if not then close immediately
    if rsv != 0:
        raise ClosedException(1002, 'RSV bit must be 0')

    if opcode == _CLOSE:
        pass
    elif opcode == _STREAM:
        pass
    elif opcode == _TEXT:
        pass
    elif opcode == _BINARY:
        pass
    elif opcode == _PONG or opcode == _PING:
        if length > 125:
            raise ClosedException(1002, 'control frame length can not be > 125')
    else:
        # unknown or reserved opcode so just close
        raise ClosedException(1002, 'unknown opcode')

    # byte
    if length <= 125:
        pass
    # short
    elif length == 126:
        short_len = await reader.readexactly(2)
        length = struct.unpack_from('!H', short_len)[0]
    #long
    elif length == 127:
        long_len = await reader.readexactly(8)
        length = struct.unpack_from('!Q', long_len)[0]
    else:
        raise ClosedException(1002, 'unknown payload length')

    if length > max_payload:
        raise ClosedException(1009, 'payload too large')

    if mask == 128:
        mask = await reader.readexactly(4)
    else:
        mask = None

    payload = b''
    if length > 0:
        payload = await reader.readexactly(length)
        if mask:
            mask_payload = mask_data(mask, payload)
            payload = mask_payload

    return bool(fin), opcode, length, payload





###########################################################################
class HTTPResponse:
    def __init__(self,status:int,content,content_type:str="text/html", headers:dict={}):
        if not isinstance(content,bytes):
            content=str(content).encode()
        self.status=status
        self.content=content
        self.headers=headers
        # overide !!!!
        self.headers["Content-Type"]=content_type
        self.headers["Content-Length"]=len(self.content)
    
    def toHTTPResponse(self) -> bytes:
        m={
            200: "OK",
            201: "CREATED",
            400: "BAD REQUEST",
            404: "NOT FOUND",
            500: "SERVER ERROR",
        }
        
        b=b"HTTP/1.1 "+str(self.status).encode()+b" "+ m.get(self.status,"UNKNOWN").encode()+ b"\n"
        for k,v in self.headers.items():
            b+=str(k).encode()+b": "+str(v).encode()+b"\n"
        b+=b"\n"
        b+=self.content
        return b
        



###########################################################################
###########################################################################
###########################################################################

if __name__=="__main__":
    host="127.0.0.1"
    port=8000

    async def handlehttp( request ) -> HTTPResponse:
        return HTTPResponse( 200, f"method: {request.method}, path: {request.path}, headers: {request.headers}" )

    async def wsserver(websocket):
        while True:
            frame = await websocket.recv()
            if frame is None:
                break
            await websocket.send(frame)

    loop = asyncio.get_event_loop()
    server = loop.run_until_complete( start_server(handlehttp, wsserver, host, port) )
    try:
        loop.run_forever()
    except KeyboardInterrupt as e:
        server.close()
        loop.run_until_complete(server.wait_closed())
    finally:
        loop.close()
