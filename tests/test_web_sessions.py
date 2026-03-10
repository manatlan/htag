import pytest
from starlette.testclient import TestClient
from starlette.requests import Request
from htag.server import WebApp
from htag import Tag

class MyApp(Tag.App):
    def __init__(self):
        super().__init__()
        self.count = 0
    def inc(self, e):
        self.count += 1

def test_multi_session_logic():
    """Verify that passing a class creates unique instances for different sids."""
    server = WebApp(MyApp)
    
    # Simulate User 1
    client1 = TestClient(server.app)
    res1 = client1.get("/")
    assert res1.status_code == 200
    sid1 = res1.cookies.get("htag_sid")
    assert sid1 is not None
    
    # Simulate User 2
    client2 = TestClient(server.app)
    res2 = client2.get("/")
    assert res2.status_code == 200
    sid2 = res2.cookies.get("htag_sid")
    assert sid2 is not None
    assert sid1 != sid2
    
    # Verify they have different instances in WebApp
    mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
    inst1 = server._get_instance(sid1, mock_req)
    inst2 = server._get_instance(sid2, mock_req)
    assert inst1 is not inst2
    assert isinstance(inst1, MyApp)
    assert isinstance(inst2, MyApp)

def test_single_instance_logic():
    """Verify that passing an instance shares it among all sids (backward compatibility)."""
    shared_app = MyApp()
    server = WebApp(shared_app)
    
    client1 = TestClient(server.app)
    res1 = client1.get("/")
    sid1 = res1.cookies.get("htag_sid")
    
    client2 = TestClient(server.app)
    res2 = client2.get("/")
    sid2 = res2.cookies.get("htag_sid")
    
    mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
    inst1 = server._get_instance(sid1, mock_req)
    inst2 = server._get_instance(sid2, mock_req)
    assert inst1 is inst2
    assert inst1 is shared_app

def test_on_instance_callback():
    """Verify that the on_instance callback is called exactly once per new instance."""
    initialized = []
    def my_init(inst):
        initialized.append(inst)
        inst.initialized = True
        
    server = WebApp(MyApp, on_instance=my_init)
    client = TestClient(server.app)
    
    # Trigger instance creation
    res = client.get("/")
    sid = res.cookies.get("htag_sid")
    mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
    inst = server._get_instance(sid, mock_req)
    
    assert inst in initialized
    assert inst.initialized is True
    assert len(initialized) == 1
    
    # Retrieval should not trigger it again
    inst_again = server._get_instance(sid, mock_req)
    assert len(initialized) == 1

def test_favicon_route():
    """Verify the silent favicon route exists."""
    server = WebApp(MyApp)
    client = TestClient(server.app)
    res = client.get("/favicon.ico")
    # It should return 200 (if logo exists) or 204 (if not)
    assert res.status_code in [200, 204]

def test_tag_request_attribute():
    """Verify that tag.request is available in __init__, on_mount and event handlers."""
    class RequestTester(Tag.App):
        def init(self):
            self.init_request = self.request
            self.mount_request = None
            self.event_request = None
            self <= Tag.button("Click me", _onclick=self.on_click, _id="btn")

        def on_mount(self):
            self.mount_request = self.request

        def on_click(self, e):
            self.event_request = self.request

    server = WebApp(RequestTester)
    client = TestClient(server.app)
    
    # 1. Initial GET (triggers init and on_mount)
    res = client.get("/")
    assert res.status_code == 200
    sid = res.cookies.get("htag_sid")
    mock_req = Request(scope={"type": "http", "headers": [], "path": "/"})
    inst = server._get_instance(sid, mock_req)
    
    assert inst.init_request is not None
    assert inst.mount_request is not None
    assert inst.init_request.scope["type"] == "http"
    
    # 2. Simulate an event (triggers on_click via HTTP POST)
    # Note: In real life, it might be WS, but WebApp supports HTTP POST for events too.
    payload = {"id": inst.childs[0].id, "event": "click", "data": {"callback_id": "123"}}
    headers = {"X-HTAG-TOKEN": inst.htag_csrf}
    res = client.post("/event", json=payload, headers=headers)

    assert res.status_code == 200
    
    # Need to wait for background task if using WebApp directly, 
    # but here we can just check if it was set since it's a simple assignment.
    # Actually server.py:409 uses asyncio.create_task, so we might need a small sleep or 
    # check if the event handler finished. In unit tests, we can call it manually to be sure.
    
    import asyncio
    async def run_event():
        await inst.handle_event(payload, None)
    
    asyncio.run(run_event())
    assert inst.event_request is not None
    assert inst.event_request.scope["type"] == "http"
