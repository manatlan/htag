import pytest
import multiprocessing
import time
import socket
import re
from playwright.sync_api import Page, expect

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port):
    from htag import Tag, WebApp
    import asyncio

    class MyApp(Tag.App):
        def init(self):
            self += Tag.button("Slow Action", _onclick=self.slow_action, id="btn")
            self += Tag.div("Ready", id="status")

        async def slow_action(self, e):
            self.childs[1].text = "Processing..."
            yield
            await asyncio.sleep(1) # Simulated delay
            self.childs[1].text = "Done"

    app = WebApp(MyApp)
    app.run(port=port, open_browser=False)

@pytest.fixture(scope="module")
def app_port():
    port = get_free_port()
    p = multiprocessing.Process(target=run_server, args=(port,))
    p.start()
    time.sleep(2)
    yield port
    p.terminate()
    p.join()

def test_interacting_class(app_port, page: Page):
    url = f"http://127.0.0.1:{app_port}"
    page.goto(url)
    
    # Body should NOT have 'interacting' initially
    expect(page.locator("body")).not_to_have_class(re.compile(r"interacting"))
    
    # Click button to trigger long action
    page.click("#btn")
    
    # Body SHOULD have 'interacting' while processing
    expect(page.locator("body")).to_have_class(re.compile(r"interacting"))
    
    # Wait for completion
    expect(page.locator("#status")).to_have_text("Done", timeout=5000)
    
    # Body should NOT have 'interacting' anymore
    expect(page.locator("body")).not_to_have_class(re.compile(r"interacting"))
