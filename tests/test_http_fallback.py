import pytest
from htag import Tag
from htag.web import WebApp
from starlette.testclient import TestClient
from htag.utils import _obf_loads, _obf_dumps

class MyTag(Tag.App):
    def init(self):
        self.btn = Tag.button("hello", _onclick=self.doit)
        self += self.btn
    def doit(self, o):
        print("=== DOIT RAN ===")
        self.btn.clear("world")

def test_pure_http_fallback():
    app = WebApp(MyTag)
    client = TestClient(app.app)
    
    # Get HTML to establish session
    resp = client.get("/")
    assert resp.status_code == 200
    
    # Extract CSRF token
    html = resp.text
    import re
    match = re.search(r'window\.HTAG_CSRF\s*=\s*"([^"]+)"', html)
    csrf = match.group(1) if match else None
    
    # Get instance to find the button ID
    sid = resp.cookies.get("htag_sid")
    instance = app.instances[sid]
    btn_id = instance.btn.id
    
    # Now simulate a pure HTTP fallback request
    payload = {
        "id": str(btn_id),
        "event": "click",
        "data": {"callback_id": "123"},
        "fallback": True
    }
    
    parano = getattr(instance, "parano_key", None)
    encoded_payload = _obf_dumps(payload, parano).encode("utf-8")
    
    headers = {"Content-Type": "application/json"}
    if csrf:
        headers["X-HTAG-TOKEN"] = csrf
        
    resp2 = client.post("/event", content=encoded_payload, headers=headers)
    assert resp2.status_code == 200
    res = resp2.json()
    assert res["status"] == "ok"
    assert "payloads" in res
    assert len(res["payloads"]) >= 1
    
    # Check the contents of the payload
    first_payload = _obf_loads(res["payloads"][0], parano)
    assert first_payload["action"] == "update"
    assert first_payload["callback_id"] == "123"
    assert str(btn_id) in first_payload["updates"]
    assert "world" in first_payload["updates"][str(btn_id)]
