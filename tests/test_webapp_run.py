import pytest
from unittest.mock import patch, MagicMock
from htag.server import WebApp
from htag import Tag
import threading

class App(Tag.App):
    def init(self):
        self += "test"

def test_webapp_run_basic():
    wa = WebApp(App)
    with patch("uvicorn.run") as mock_run:
        wa.run(port=8001, open_browser=False, exit_on_disconnect=False)
        assert mock_run.called
        args, kwargs = mock_run.call_args
        assert kwargs["port"] == 8001
        assert wa.exit_on_disconnect is False

def test_webapp_run_with_flags():
    wa = WebApp(App)
    with patch("uvicorn.run") as mock_run, \
         patch("webbrowser.open") as mock_open, \
         patch("threading.Thread") as mock_thread:
        
        wa.run(port=8001, open_browser=True, exit_on_disconnect=True)
        
        assert mock_run.called
        assert wa.exit_on_disconnect is True
        assert mock_thread.called
        
        # Check that threading.Thread was called with a target that eventually calls webbrowser.open
        # We can simulate the thread target execution
        target = mock_thread.call_args[1]["target"]
        with patch("time.sleep"): # avoid delay in tests
            target()
        assert mock_open.called
        assert "http://127.0.0.1:8001" in mock_open.call_args[0][0]

def test_webapp_run_exit_on_disconnect_propagation():
    wa = WebApp(App)
    with patch("uvicorn.run"):
        wa.run(exit_on_disconnect=True, open_browser=False) # Sets it on WebApp
    
    # Simulate session creation
    mock_request = MagicMock()
    mock_request.cookies = {"htag_sid": "sid123"}
    inst = wa._get_instance("sid123", mock_request)
    
    assert inst.exit_on_disconnect is True
    assert getattr(inst, "_webserver") == wa
