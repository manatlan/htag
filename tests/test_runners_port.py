import pytest
from unittest.mock import patch, MagicMock
from htag import Tag, WebApp, ChromeApp
import os

class App(Tag.App):
    def init(self) -> None:
        self += "Hello"

def test_webapp_resolve_port_zero():
    # Reset HTAG_PORT just in case
    if "HTAG_PORT" in os.environ:
        del os.environ["HTAG_PORT"]
        
    with patch("uvicorn.run") as mock_run:
        wa = WebApp(App)
        # Call run with port 0 and no browser opening (to avoid delays/errors)
        wa.run(port=0, open_browser=False)
        
        args, kwargs = mock_run.call_args
        # kwargs['port'] should not be 0 anymore
        resolved_port = kwargs['port']
        assert resolved_port > 0
        assert isinstance(resolved_port, int)
        
        # Ensure it was stored in the env for reloader
        assert os.environ["HTAG_PORT"] == str(resolved_port)

def test_webapp_use_htag_port_env():
    # Simulate a reloader child process
    os.environ["HTAG_PORT"] = "12345"
    
    with patch("uvicorn.run") as mock_run:
        wa = WebApp(App)
        wa.run(port=0, open_browser=False)
        
        args, kwargs = mock_run.call_args
        assert kwargs['port'] == 12345
        
    del os.environ["HTAG_PORT"]

def test_chromeapp_resolve_port_zero_logic():
    # ChromeApp.run is a bit more complex, we want to check that the port 
    # used by uvicorn is the same resolved by the socket logic.
    if "HTAG_PORT" in os.environ:
       del os.environ["HTAG_PORT"]

    with patch("uvicorn.run") as mock_run:
        with patch("subprocess.Popen") as mock_popen: # mock browser launch
            ca = ChromeApp(App, kiosk=False)
            ca.run(port=0) # will launch uvicorn.run
            
            args, kwargs = mock_run.call_args
            resolved_port = kwargs['port']
            assert resolved_port > 0
            assert os.environ["HTAG_PORT"] == str(resolved_port)

    del os.environ["HTAG_PORT"]
