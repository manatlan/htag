import pytest
import asyncio
from typing import AsyncGenerator, Iterator

from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from htag import App, Tag
from htag.web import WebApp

class AppWithYields(App):
    def init(self):
        self += Tag.div("init", _id="status")
        
    def on_mount(self) -> Iterator[str]:
        self.clear()
        self += Tag.div("loading...", _id="status")
        yield "update1"
        self.clear()
        self += Tag.div("done", _id="status")
        yield "update2"

@pytest.mark.asyncio
async def test_on_mount_yields_websocket():
    web = WebApp(AppWithYields)
    
    with TestClient(web.app) as client:
        # 1. Initial page load (no websocket yet, on_mount generator should be queued)
        response = client.get("/")
        assert response.status_code == 200
        assert "status" in response.text
        assert "init" in response.text # initial state before yields are consumed
        
        # 2. Connect websocket
        with client.websocket_connect("/ws") as websocket:
            # First message received is the initial broadcast
            data = websocket.receive_text()
            assert "update" in data or "init" in data
            
            # The pending generators are consumed, wait for the broadcast updates
            # update1 (loading...)
            data = websocket.receive_text()
            assert "loading..." in data
            
            # update2 (done)
            data = websocket.receive_text()
            assert "done" in data

@pytest.mark.asyncio
async def test_on_mount_yields_sse():
    web = WebApp(AppWithYields)
    
    with TestClient(web.app) as client:
        # 1. Initial page load
        response = client.get("/")
        assert response.status_code == 200
        sid = response.cookies.get("htag_sid")
        
        # 2. Extract app instance
        instance = web.instances[sid]
        
        # 3. Simulate _handle_sse
        from starlette.requests import Request
        
        class MockRequest:
            cookies = {"htag_sid": sid}
            async def is_disconnected(self):
                return False
                
        req = MockRequest()
        
        gen = instance._handle_sse(req)
        
        # Pull the first 'initial' payload + triggers background flush
        initial_chunk = await gen.__anext__()
        assert "data:" in initial_chunk
        assert "loading..." not in initial_chunk # Pending update not yet given
        
        # To let the created task flush the items to the queue, yield control
        await asyncio.sleep(0.01)
        
        # Pull first queued yield
        q1 = await gen.__anext__()
        assert "loading..." in q1
        
        # Pull second queued yield
        q2 = await gen.__anext__()
        assert "done" in q2
        
        # Cleanup tasks
        instance.sse_queues.clear()
