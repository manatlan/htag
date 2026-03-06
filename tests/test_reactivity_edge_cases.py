import asyncio
import pytest
from htag.core import GTag, State
from htag import Tag
from htag.server import AppRunner as App

def test_boolean_attributes_edge_cases():
    """Test boolean attribute rendering in GTag (branches 65, 67 in core.py)"""
    # True should render only the name
    t1 = Tag.button(_disabled=True)
    assert ' disabled id="' in str(t1)
    
    # False should omit the attribute
    t2 = Tag.button(_disabled=False)
    assert ' disabled' not in str(t2)
    
    # Reactive True
    s = State(True)
    t3 = Tag.button(_disabled=lambda: s.value)
    assert ' disabled' in str(t3)
    
    # Reactive False
    s.value = False
    assert ' disabled' not in str(t3)

def test_state_set_method():
    """Test the new State.set() method"""
    s = State(10)
    res = s.set(20)
    assert s.value == 20
    assert res == 20 # returns the value

def test_recursive_statics_and_js_collection():
    """Test collection of statics/js from rendered callables (server.py)"""
    class MyComp(Tag.div):
        statics = ".mycomp { color: red; }"
        def init(self):
            self.call_js("console.log('comp ready')")
            self.text = "Comp"

    class MyApp(App):
        def init(self):
            # MyComp is inside a lambda
            Tag.add(lambda: MyComp())
    
    app = MyApp()
    html = app._render_page()
    
    # Verify statics are in the initial page
    assert ".mycomp { color: red; }" in html
    
    # Verify JS calls are collected during (re)render
    updates = {}
    js_calls = []
    app.collect_updates(app, updates, js_calls)
    assert "console.log('comp ready')" in js_calls

@pytest.mark.asyncio
async def test_async_event_handler():
    """Test async callback in App (server.py branch 458)"""
    class MyApp(App):
        async def my_handler(self, e):
            self.result = "done"
            return "ok"
            
        def init(self):
            self.btn = Tag.button("Click", _onclick=self.my_handler)
            self.result = None

    app = MyApp()
    msg = {"id": app.btn.id, "event": "click", "data": {"callback_id": "123"}}
    await app.handle_event(msg, None)
    assert app.result == "done"

@pytest.mark.asyncio
async def test_generator_event_handler():
    """Test generator as event handler (server.py branch 506-511)"""
    class MyApp(App):
        def my_gen(self, e):
            self.step = 1
            yield
            self.step = 2
            return "final"
            
        def init(self):
            self.btn = Tag.button("Click", _onclick=self.my_gen)
            self.step = 0

    app = MyApp()
    # We need to mock broadcast_updates to avoid network calls
    broadcasts = []
    async def mock_broadcast(result=None, callback_id=None):
        broadcasts.append((result, callback_id))
    app.broadcast_updates = mock_broadcast
    
    msg = {"id": app.btn.id, "event": "click", "data": {"callback_id": "123"}}
    await app.handle_event(msg, None)
    
    assert app.step == 2
    # Broadcast called twice: once for yield, once for return
    assert len(broadcasts) == 2
    assert broadcasts[1] == ("final", "123")

def test_event_getattr_none():
    """Test Event.__getattr__ returns None (server.py branch 29)"""
    from htag.server import Event
    e = Event(Tag.div(), {"event": "click"})
    assert e.non_existent_attr is None

@pytest.mark.asyncio
async def test_async_generator_event_handler():
    """Test async generator as event handler (server.py branch 479-482)"""
    class MyApp(App):
        async def my_agen(self, e):
            self.step = 1
            yield
            self.step = 2
            
        def init(self):
            self.btn = Tag.button("Click", _onclick=self.my_agen)
            self.step = 0

    app = MyApp()
    broadcasts = []
    async def mock_broadcast(result=None, callback_id=None):
        broadcasts.append((result, callback_id))
    app.broadcast_updates = mock_broadcast
    
    msg = {"id": app.btn.id, "event": "click", "data": {"callback_id": "123"}}
    await app.handle_event(msg, None)
    
    assert app.step == 2
    assert len(broadcasts) == 2

@pytest.mark.asyncio
async def test_event_handler_error_reporting():
    """Test error reporting in event handlers (server.py branch 490-513)"""
    class MyApp(App):
        def crashing_handler(self, e):
            raise ValueError("Boom")
            
        def init(self):
            self.btn = Tag.button("Click", _onclick=self.crashing_handler)

    app = MyApp()
    
    # Test WebSocket error reporting
    class MockWS:
        def __init__(self): self.sent = []
        async def send_text(self, text): self.sent.append(text)
    
    ws = MockWS()
    msg = {"id": app.btn.id, "event": "click", "data": {"callback_id": "123"}}
    await app.handle_event(msg, ws)
    
    assert len(ws.sent) == 1
    assert "Boom" in ws.sent[0]
    
    # Test SSE fallback error reporting
    app.sse_queues = {asyncio.Queue()}
    await app.handle_event(msg, None)
    q = list(app.sse_queues)[0]
    err = await q.get()
    assert "Boom" in err

@pytest.mark.asyncio
async def test_invalid_tag_id():
    """Test handle_event with invalid tag_id (server.py branch 458)"""
    app = App()
    res = await app.handle_event({"id": 123}, None) # int instead of str
    assert res is None

def test_eval_child_non_stringify():
    """Test _eval_child with stringify=False (core.py branch 335)"""
    t = Tag.div()
    val = t._eval_child(True, stringify=False)
    assert val is True
    val_str = t._eval_child(True, stringify=True)
    assert val_str == "True"
