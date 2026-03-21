import pytest
from typing import Iterator
from starlette.testclient import TestClient
from htag import App, Tag
from htag.web import WebApp

class UnmountingComponent(Tag.div):
    def on_mount(self):
        self.app_root = self.root

    def on_unmount(self) -> Iterator[str]:
        # Generators evaluate lazily, so we use the stored app_root
        self.app_root.unmounted_triggered += 1
        self.app_root.status.clear(str(self.app_root.unmounted_triggered))
        yield "update1"
        self.app_root.unmounted_triggered += 1
        self.app_root.status.clear(str(self.app_root.unmounted_triggered))
        yield "update2"

class AppWithUnmount(App):
    def init(self):
        self.unmounted_triggered = 0
        self.comp = UnmountingComponent("I will go away")
        self += self.comp
        
        self.btn = Tag.button("Remove It", _onclick=self.do_remove, _id="btn")
        self += self.btn
        
        # UI element to track state
        self.status = Tag.div(self.unmounted_triggered, _id="status")
        self += self.status

    def do_remove(self, o):
        self.comp.remove()
        
    def render_initial(self):
        # ensure status is up-to-date
        self.status.clear(str(self.unmounted_triggered))
        return super().render_initial()

@pytest.mark.asyncio
async def test_on_unmount_yields_websocket():
    web = WebApp(AppWithUnmount)
    
    with TestClient(web.app) as client:
        # 1. Initial page load
        response = client.get("/")
        assert response.status_code == 200
        
        # 2. Connect websocket
        with client.websocket_connect("/ws") as websocket:
            # First message received is the initial broadcast
            data = websocket.receive_text()
            assert "I will go away" in data
            
            # 3. Simulate clicking the "Remove It" button
            # We construct a fake message mimicking the browser sending the event
            msg = {
                "id": "btn",
                "event": "click",
                "data": {"callback_id": "cb1"}
            }
            # We have to obfuscate if parano_key is used, but by default it isn't
            websocket.send_json(msg)
            
            # The click event will call do_remove()
            # Which calls self.comp.remove() -> _trigger_unmount()
            # The unmount yields twice, and we expect 3 payloads total or 2
            # because the event handler completes, so the runner will send the first broadcast
            # THEN it flushes pending generators
            
            # payload 1: Component removed (HTML delta), callback_id='cb1'
            data = websocket.receive_text()
            assert "cb1" in data # event resolution
            
            # payload 2: First yield in on_unmount
            data = websocket.receive_text()
            assert "update" in data # action: update
            assert "1" in data # from the counter 1
            
            # payload 3: Second yield in on_unmount
            data = websocket.receive_text()
            assert "update" in data
            assert "2" in data # from counter 2
