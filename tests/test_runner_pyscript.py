import pytest
from htag.runners import PyScript
from htag.server import AppRunner as App

def test_pyscript_runner_initializes(monkeypatch):
    class FakeJS:
        class window:
            py_htag_event = None
            _error_overlay = None
            def handle_payload(data):
                pass
        class document:
            class body:
                outerHTML = ""
                def appendChild(node):
                    pass
        def eval(code):
            pass
            
    monkeypatch.setattr("htag.runners.pyscript.js", FakeJS)

    class MyApp(App):
        pass
        
    runner = PyScript(MyApp)
    runner.run()
    assert runner.app is not None
