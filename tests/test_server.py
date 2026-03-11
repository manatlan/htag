import pytest
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from htag.server import Event, WebApp
from htag import Tag

App = Tag.App # Alias for tests

def test_event_logic():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "click",
        "data": {"value": "hello", "x": 10}
    }
    e = Event(target, msg)
    assert e.target == target
    assert e.id == "123"
    assert e.name == "click"
    assert e.value == "hello"
    assert e.x == 10
    assert "Event(click" in str(e)

def test_app_find_tag():
    app = App()
    child = Tag.div()
    app += child
    
    assert app.find_tag(app, app.id) == app
    assert app.find_tag(app, child.id) == child
    assert app.find_tag(app, "nonexistent") is None

def test_app_collect_statics():
    class Comp(Tag.div):
        statics = "/* css */"
    
    app = App()
    app.statics = Tag.style("body { color: red }")
    app += Comp()
    
    statics = []
    app.collect_statics(app, statics)
    assert any("/* css */" in s for s in statics)
    assert any("body { color: red }" in s for s in statics)

def test_app_collect_updates():
    app = App()
    child = Tag.div("initial")
    app += child
    
    # Initially dirty because of creation
    updates = {}
    js = []
    app.collect_updates(app, updates, js)
    assert app.id in updates
    assert child.id not in updates # Child is inside app's render
    
    # Mark child as dirty
    child.clear() 
    app._GTag__dirty = False # Reset app
    updates = {}
    app.collect_updates(app, updates, js)
    assert child.id in updates
    assert app.id not in updates

@pytest.mark.asyncio
async def test_app_handle_event_sync():
    app = App()
    shared = {"done": False}
    def my_cb(e):
        shared["done"] = True
        return "result"
    
    btn = Tag.button(_onclick=my_cb)
    app += btn
    
    ws = AsyncMock()
    app.websockets.add(ws)
    msg = {"id": btn.id, "event": "click", "data": {"callback_id": "cb1"}}
    
    await app.handle_event(msg, ws)
    assert shared["done"] is True
    # Check if ws received the update with result
    calls = ws.send_text.call_args_list
    found = False
    for call in calls:
        data = json.loads(call[0][0])
        if data.get("callback_id") == "cb1" and data.get("result") == "result":
            found = True
    assert found

@pytest.mark.asyncio
async def test_app_handle_event_async():
    app = App()
    shared = {"done": False}
    async def my_cb(e):
        await asyncio.sleep(0.01)
        shared["done"] = True
    
    btn = Tag.button(_onclick=my_cb)
    app += btn
    
    ws = AsyncMock()
    msg = {"id": btn.id, "event": "click", "data": {}}
    
    await app.handle_event(msg, ws)
    assert shared["done"] is True

@pytest.mark.asyncio
async def test_app_handle_event_generator():
    app = App()
    def my_gen(e):
        app.call_js("1")
        yield
        app.call_js("2")
        yield
        app.call_js("3")
        return "final"
    
    btn = Tag.button(_onclick=my_gen)
    app += btn
    
    ws = AsyncMock()
    app.websockets.add(ws)
    msg = {"id": btn.id, "event": "click", "data": {"callback_id": "gen1"}}
    
    await app.handle_event(msg, ws)
    # Should have called broadcast_updates multiple times
    # 2 for yields + 1 for final
    assert ws.send_text.call_count >= 3
    
    last_call = json.loads(ws.send_text.call_args_list[-1][0][0])
    assert last_call["callback_id"] == "gen1"
    assert last_call["result"] == "final"

@pytest.mark.asyncio
async def test_app_handle_event_error():
    app = App()
    def fail(e):
        raise ValueError("boom")
    
    btn = Tag.button(_onclick=fail)
    app += btn
    
    ws = AsyncMock()
    msg = {"id": btn.id, "event": "click", "data": {"callback_id": "error1"}}
    
    await app.handle_event(msg, ws)
    # Should send an error payload
    data = json.loads(ws.send_text.call_args[0][0])
    assert data["action"] == "error"
    assert "boom" in data["traceback"]
    assert data["callback_id"] == "error1"

@pytest.mark.asyncio
async def test_app_handle_event_error_stdout(capsys):
    app = App()
    def fail(e):
        raise ValueError("stdout boom")
    
    btn = Tag.button(_onclick=fail)
    app += btn
    
    ws = AsyncMock()
    msg = {"id": btn.id, "event": "click", "data": {}}
    
    await app.handle_event(msg, ws)
    
    captured = capsys.readouterr()
    assert "ValueError: stdout boom" in captured.out

@pytest.mark.asyncio
async def test_app_handle_event_async_error():
    app = App()
    async def async_fail(e):
        await asyncio.sleep(0.01)
        raise RuntimeError("async boom")
        
    btn = Tag.button(_onclick=async_fail)
    app += btn
    
    ws = AsyncMock()
    msg = {"id": btn.id, "event": "click", "data": {"callback_id": "error_async1"}}
    
    await app.handle_event(msg, ws)
    data = json.loads(ws.send_text.call_args[0][0])
    assert data["action"] == "error"
    assert "async boom" in data["traceback"]
    assert data["callback_id"] == "error_async1"

@pytest.mark.asyncio
async def test_app_handle_event_error_sse_fallback():
    app = App()
    def fail(e):
        raise ValueError("sse boom")
        
    btn = Tag.button(_onclick=fail)
    app += btn
    
    # Client has only SSE connected (ws is None like in HTTP POST fallback)
    queue = asyncio.Queue()
    app.sse_queues.add(queue)
    
    msg = {"id": btn.id, "event": "click", "data": {"callback_id": "error_sse1"}}
    
    await app.handle_event(msg, None)
    
    # We expect the payload in the queue
    payload = queue.get_nowait()
    data = json.loads(payload)
    assert data["action"] == "error"
    assert "sse boom" in data["traceback"]
    assert data["callback_id"] == "error_sse1"

def test_app_render_page():
    app = App()
    html = app._render_page()
    assert "<!DOCTYPE html>" in html
    assert app.__class__.__name__ in html
    assert app.id in html

def test_app_render_page_error():
    app = App()
    def crash(): raise ValueError("initial view crash")
    app <= crash
    html = app._render_page()
    assert "Initial Render Error" in html
    assert "initial view crash" in html
    assert "Internal Server Error" not in html
    
    app.debug = False
    html = app._render_page()
    assert "Internal Server Error" in html

@pytest.mark.asyncio
async def test_broadcast_updates():
    app = App()
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    app.websockets.add(ws1)
    app.websockets.add(ws2)
    
    app.call_js("alert(1)")
    await app.broadcast_updates()
    
    for ws in [ws1, ws2]:
        data = json.loads(ws.send_text.call_args[0][0])
        assert data["js"] == ["alert(1)"]

    # Test dead client removal
    ws2.send_text.side_effect = Exception("dead")
    app.call_js("alert(2)")
    await app.broadcast_updates()
    assert ws2 not in app.websockets

@pytest.mark.asyncio
async def test_broadcast_updates_render_error():
    app = App()
    ws = AsyncMock()
    app.websockets.add(ws)
    
    app._GTag__dirty = True
    def crashing_render():
        raise TypeError("Render crash simulation")
    app <= crashing_render
    
    await app.broadcast_updates(callback_id="123")
    
    data = json.loads(ws.send_text.call_args[0][0])
    assert data["action"] == "error"
    assert "Render crash simulation" in data["traceback"]
    assert data["callback_id"] == "123"

def test_app_property():
    app = App()
    from starlette.applications import Starlette
    assert isinstance(app.app, Starlette)

@pytest.mark.asyncio
async def test_app_handle_event_value_sync():
    app = App()
    inp = Tag.input(value="old")
    app += inp
    
    ws = AsyncMock()
    msg = {"id": inp.id, "event": "input", "data": {"value": "new"}}
    await app.handle_event(msg, ws)
    assert inp["value"] == "new"

@pytest.mark.asyncio
async def test_app_handle_event_async_generator():
    app = App()
    async def my_agen(e):
        app.call_js("a")
        yield
        app.call_js("b")
        yield
        
    btn = Tag.button(_onclick=my_agen)
    app += btn
    
    ws = AsyncMock()
    app.websockets.add(ws)
    msg = {"id": btn.id, "event": "click", "data": {}}
    
    await app.handle_event(msg, ws)
    assert ws.send_text.call_count >= 2

@pytest.mark.asyncio
async def test_app_handle_event_gtag_result():
    app = App()
    def my_cb(e):
        return e.target # Returns a GTag
        
    btn = Tag.button(_onclick=my_cb)
    app += btn
    
    ws = AsyncMock()
    app.websockets.add(ws)
    msg = {"id": btn.id, "event": "click", "data": {"callback_id": "gt1"}}
    
    await app.handle_event(msg, ws)
    last_call = json.loads(ws.send_text.call_args_list[-1][0][0])
    assert last_call["result"] is True

def test_render_tag_special_cases():
    from htag.server import AppRunner as App
    app = App()
    
    # Ensure the auto-injected oninput is there
    inp = Tag.input()
    app += inp
    app.render_initial()
    assert "oninput" in inp._GTag__attrs
    assert "htag_event" in inp._GTag__attrs["oninput"]
    
    # prevent/stop decorators
    from htag import prevent, stop
    @prevent
    @stop
    def my_cb(e): pass
    
    btn = Tag.button("ok", _onclick=my_cb)
    html = app.render_tag(btn)
    assert "event.preventDefault()" in html
    assert "event.stopPropagation()" in html

@pytest.mark.asyncio
async def test_handle_websocket_lifecycle():
    from starlette.websockets import WebSocketDisconnect
    import os
    app = App()
    app.exit_on_disconnect = True
    
    # 1. Success case + exit
    import asyncio
    from unittest.mock import patch
    real_sleep = asyncio.sleep
    async def fast_sleep(x): await real_sleep(0)
    
    ws = AsyncMock()
    ws.receive_text.side_effect = [
        json.dumps({"id": app.id, "event": "click", "data": {}}),
        WebSocketDisconnect()
    ]
    with patch("htag.runner.os._exit") as mock_exit, \
         patch("htag.runner.asyncio.sleep", side_effect=fast_sleep):
        await app._handle_websocket(ws)
        await real_sleep(0.1) # Yield to background tasks
        assert mock_exit.called

    # 2. Multi-session case (one active session prevents exit)
    ws2 = AsyncMock()
    ws2.receive_text.side_effect = WebSocketDisconnect()
    app2 = App()
    app.exit_on_disconnect = True
    app2.websockets.add(AsyncMock()) # Another active session
    
    server = MagicMock()
    server.instances = {"sid1": app, "sid2": app2}
    app.htag_webserver = server
    
    with patch("htag.runner.os._exit") as mock_exit, \
         patch("htag.runner.asyncio.sleep", side_effect=fast_sleep):
        await app._handle_websocket(ws2)
        await real_sleep(0.1)
        assert not mock_exit.called

    # 3. Browser cleanup case
    ws3 = AsyncMock()
    ws3.receive_text.side_effect = WebSocketDisconnect()
    app3 = App()
    app3.exit_on_disconnect = True
    app3._browser_cleanup = MagicMock()
    with patch("htag.runner.os._exit") as mock_exit, \
         patch("htag.runner.asyncio.sleep", side_effect=fast_sleep):
        await app3._handle_websocket(ws3)
        await real_sleep(0.1)
        assert app3._browser_cleanup.called

    # 4. Initial send failure case
    ws4 = AsyncMock()
    ws4.send_text.side_effect = Exception("error")
    ws4.receive_text.side_effect = WebSocketDisconnect()
    await app._handle_websocket(ws4)
    assert ws4 not in app.websockets

    # 5. exit_on_disconnect = False
    ws5 = AsyncMock()
    ws5.receive_text.side_effect = WebSocketDisconnect()
    app5 = App()
    app5.exit_on_disconnect = False
    await app5._handle_websocket(ws5)
    # Just verify it doesn't crash and completes

@pytest.mark.asyncio
async def test_websocket_route_coverage():
    from htag.server import WebApp
    from starlette.testclient import TestClient
    
    server = WebApp(App)
    client = TestClient(server.app)
    
    # Need to get a session first to have the cookie
    res = client.get("/")
    assert res.status_code == 200
    
    # Test the WS route via TestClient
    with client.websocket_connect("/ws") as websocket:
        # It should send initial state immediately
        data = websocket.receive_json()
        assert data["action"] == "update"
