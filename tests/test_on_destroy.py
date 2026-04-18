import pytest
import asyncio
import time
from httpx import AsyncClient, ASGITransport
from htag import Tag, WebApp

class MyApp(Tag.App):
    def init(self):
        self.destroyed = False
        
    def on_destroy(self):
        self.destroyed = True
        
class MyAsyncApp(Tag.App):
    def init(self):
        self.async_destroyed = False
        
    async def on_destroy(self):
        await asyncio.sleep(0.1)
        self.async_destroyed = True

@pytest.mark.asyncio
async def test_on_destroy_with_reset_param():
    """Verify that ?n triggers on_destroy."""
    server = WebApp(MyApp)
    async with AsyncClient(transport=ASGITransport(app=server.app), base_url="http://test") as client:
        # Initial request
        res = await client.get("/")
        sid = res.cookies.get("htag_sid")
        
        # Get instance
        from starlette.requests import Request
        mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
        inst1 = server._get_instance(sid, mock_req)
        assert inst1.destroyed is False
        
        # Reset request
        res = await client.get("/?n")
        assert inst1.destroyed is True
        
        # Verify new instance
        inst2 = server._get_instance(sid, mock_req)
        assert inst2 is not inst1
        assert inst2.destroyed is False

@pytest.mark.asyncio
async def test_on_destroy_async_with_reset_param():
    """Verify that ?n triggers async on_destroy."""
    server = WebApp(MyAsyncApp)
    async with AsyncClient(transport=ASGITransport(app=server.app), base_url="http://test") as client:
        # Initial request
        res = await client.get("/")
        sid = res.cookies.get("htag_sid")
        
        # Get instance
        from starlette.requests import Request
        mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
        inst1 = server._get_instance(sid, mock_req)
        
        # Reset request
        res = await client.get("/?n")
        
        # Need to wait a bit for async task
        await asyncio.sleep(0.2)
        assert inst1.async_destroyed is True

@pytest.mark.asyncio
async def test_on_destroy_not_called_on_f5():
    """Verify that normal refresh does NOT trigger on_destroy."""
    server = WebApp(MyApp)
    async with AsyncClient(transport=ASGITransport(app=server.app), base_url="http://test") as client:
        # Initial request
        res = await client.get("/")
        sid = res.cookies.get("htag_sid")
        
        from starlette.requests import Request
        mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
        inst1 = server._get_instance(sid, mock_req)
        
        # Refresh request (no ?n)
        res = await client.get("/")
        assert inst1.destroyed is False
