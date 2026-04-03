from starlette.testclient import TestClient
from htag import App
from htag.web import WebApp

class MyApp(App):
    def init(self):
        self += "Hello World"

def test_htag_mode_default():
    """Verify that by default, no protocol mocking is injected."""
    webapp = WebApp(MyApp)
    client = TestClient(webapp.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "window.WebSocket=window.EventSource" not in response.text
    assert "Hello World" in response.text

def test_htag_mode_http():
    """Verify protocol mocking for 'http' mode."""
    webapp = WebApp(MyApp)
    client = TestClient(webapp.app)
    response = client.get("/", cookies={"htag_mode": "http"})
    assert response.status_code == 200
    # Both WebSocket and EventSource should be mocked
    assert "window.WebSocket=window.EventSource=class{" in response.text
    assert "new Event('error')" in response.text

def test_htag_mode_sse():
    """Verify protocol mocking for 'sse' mode."""
    webapp = WebApp(MyApp)
    client = TestClient(webapp.app)
    response = client.get("/", cookies={"htag_mode": "sse"})
    assert response.status_code == 200
    # Only WebSocket should be mocked
    assert "window.WebSocket=class{" in response.text
    assert "window.EventSource=class{" not in response.text
    assert "new Event('error')" in response.text

def test_htag_mode_invalid():
    """Verify that invalid cookie values are ignored."""
    webapp = WebApp(MyApp)
    client = TestClient(webapp.app)
    response = client.get("/", cookies={"htag_mode": "invalid"})
    assert response.status_code == 200
    assert "window.WebSocket=function()" not in response.text
    assert "window.EventSource=function()" not in response.text
