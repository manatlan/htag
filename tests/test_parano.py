import pytest
import json
import base64
from htag import Tag
from htag.server import WebApp, _obf_dumps, _obf_loads
from starlette.testclient import TestClient

App = Tag.App

class MyApp(App):
    def init(self):
        self += Tag.div("Hello Parano", id="t1")
        self += Tag.button("Click", _onclick=self.do_click, id="b1")

    def do_click(self):
        self.childs[0].clear("Clicked Parano")


def test_parano_cipher():
    obj = {"hello": "world", "x": 42}
    key = "secret123"
    
    encoded = _obf_dumps(obj, key)
    assert encoded != json.dumps(obj)
    assert isinstance(encoded, str)
    
    decoded = _obf_loads(encoded, key)
    assert decoded == obj


def test_webapp_parano_mode():
    app_host = WebApp(MyApp, parano=True)
    assert app_host.parano_key is not None
    assert len(app_host.parano_key) > 0
    
    client = TestClient(app_host.app)
    
    # 1) Get HTML to fetch initial parano state
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    
    assert "window.PARANO" in html
    assert f'"{app_host.parano_key}"' in html
    assert "Hello Parano" in html

    # Find the session cookie
    cookies = response.cookies
    assert "htag_sid" in cookies
    
    # 2) Trigger an event via fallback POST
    # We must encrypt the payload ourselves using the exact logic
    payload_obj = {"id": "b1", "event": "click"}
    encoded_payload = _obf_dumps(payload_obj, app_host.parano_key)
    
    resp_post = client.post("/event", content=encoded_payload.encode('utf-8'))
    assert resp_post.status_code == 200
    assert resp_post.json() == {"status": "ok"}
