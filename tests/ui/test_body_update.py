import pytest
import os
import sys
import multiprocessing
import time
import socket
import re

from playwright.sync_api import Page, expect

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port):
    from htag import Tag
    from htag.server import WebApp
    
    class App(Tag.App):
        def init(self):
            self.call = 0
            self.btn = Tag.button("Update Body", _onclick=self.update_body)
            self += self.btn
            self["class"] = "initial-class"
            self["data-test"] = "foo"

        def update_body(self, ev):
            self.call += 1
            self["class"] = f"updated-class-{self.call}"
            self["data-test"] = "bar"
            # Remove an old attribute and add a new one, to test attribute syncing
            del self["data-test"]
            self["data-new"] = "baz"
            self += Tag.div(f"Call {self.call}", _class="result-div")

    app = WebApp(App)
    app.run(port=port, open_browser=False)

@pytest.fixture(scope="module")
def app_port():
    port = get_free_port()
    p = multiprocessing.Process(target=run_server, args=(port,))
    p.start()
    
    # Wait for server to start
    time.sleep(3)
    
    yield port
    
    p.terminate()
    p.join()

def test_body_update_no_dom_exception(app_port, page: Page):
    """
    This test verifies that updating the <body> tag triggers the 
    DOMParser fallback in client_js.py and doesn't throw a DOMException
    when reassigning outerHTML on document.body.
    """
    url = f"http://127.0.0.1:{app_port}"
    page.goto(url)
    
    # Trap page errors to explicitly fail if DOMException occurs
    errors = []
    page.on("pageerror", lambda err: errors.append(err))
    
    # Check initial state
    body = page.locator("body")
    expect(body).to_have_class(re.compile(r".*initial-class.*"))
    
    # Click to update body
    page.click("button:has-text('Update Body')")
    
    # Verification: Did the innerHTML update?
    expect(page.locator("text=Call 1")).to_be_visible()
    
    # Verification: Did the classes update?
    expect(body).to_have_class(re.compile(r".*updated-class-1.*"))
    
    # Verification: Attributes synced properly?
    # Playwright locator.get_attribute
    assert body.get_attribute("data-new") == "baz"
    assert body.get_attribute("data-test") is None
    
    # Ensure no unhandled JS exceptions occurred!
    assert len(errors) == 0, f"Javascript errors found: {errors}"

    # Click again to ensure multiple updates work smoothly
    page.click("button:has-text('Update Body')")
    expect(page.locator("text=Call 2")).to_be_visible()
    expect(body).to_have_class(re.compile(r".*updated-class-2.*"))
    assert len(errors) == 0
