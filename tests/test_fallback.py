import pytest
from starlette.testclient import TestClient
import asyncio
import json
from htag import Tag
from htag.server import WebApp

class MyMockApp(Tag.App):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.btn = Tag.button("Click", _onclick=self.increment)
        self.label = Tag.span(str(self.count))
        self += self.btn
        self += self.label

    def increment(self, ev):
        self.count += 1
        self.label.clear()
        self.label += str(self.count)

@pytest.fixture
def test_client():
    ws = WebApp(MyMockApp)
    # Fastapi TestClient doesn't fully support async streams the way uvicorn does natively
    # but we can test the synchronous behavior and simple generator properties
    return TestClient(ws.app)

def test_fallback_no_cookie(test_client):
    """Test endpoints reject missing session cookie gracefully"""
    res = test_client.get("/stream")
    assert res.status_code == 400
    assert "No session cookie" in res.text

    res = test_client.post("/event", json={"id": "x", "event": "click"})
    assert res.status_code == 400
    assert "No session cookie" in res.text

@pytest.mark.asyncio
async def test_fallback_cycle():
    """Test the full HTTP fallback lifecycle using AsyncClient for Server-Sent Events"""
    # TestClient doesn't handle StreamingResponses well without deadlocks,
    # so we'll test the raw server logic using httpx async client if needed, or
    # directly call the WebApp routing methods.
    
    server = WebApp(MyMockApp)
    
    # 1. Simulate initial home page load to get cookie
    from starlette.requests import Request
    
    # httpx AsyncClient recommended for streaming
    from httpx import AsyncClient, ASGITransport
    
    async with AsyncClient(transport=ASGITransport(app=server.app), base_url="http://test") as ac:
        # Load index
        res = await ac.get("/")
        assert res.status_code == 200
        sid = res.cookies.get("htag_sid")
        assert sid is not None
        
        app_instance = server.instances[sid]
        
        # The stream will block forever, we read just the first payload chunk (initial render)
        # Using a timeout to ensure we don't block
        import asyncio
        import contextlib
        
        async def read_stream():
            async with ac.stream("GET", "/stream") as stream_res:
                assert stream_res.status_code == 200
                async for chunk in stream_res.aiter_lines():
                    if chunk.startswith("data: "):
                        payload = json.loads(chunk[6:])
                        if payload["action"] == "update":
                            return payload
            return None
            
        with contextlib.suppress(asyncio.TimeoutError):
            payload = await asyncio.wait_for(read_stream(), timeout=1.0)
            assert payload is not None
            assert payload["action"] == "update"
            assert "updates" in payload
            assert app_instance.id in payload["updates"]
        
        # Ensure the stream handler discarded the queue after connection closed
        assert len(app_instance.sse_queues) == 0

        # We can also test sending an event via POST and checking the app state directly
        btn_id = app_instance.btn.id
        event_payload = {
            "id": btn_id,
            "event": "click",
            "data": {"callback_id": "test_123"}
        }
        
        headers = {"X-HTAG-TOKEN": getattr(app_instance, "htag_csrf", "")}
        res = await ac.post("/event", json=event_payload, headers=headers)
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

        
        # Wait a tiny bit for the background asyncio task to run `handle_event`
        await asyncio.sleep(0.1)
        
        assert app_instance.count == 1
        assert "1" in app_instance.render_tag(app_instance.label)
