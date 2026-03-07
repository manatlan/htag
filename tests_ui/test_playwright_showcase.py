import pytest
import os
import sys
import multiprocessing
import time
import socket
import re

from playwright.sync_api import Page, expect

# Ensure root directory is in sys.path so we can import 'test.py'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port):
    from test import Showcase
    from htag.server import WebApp
    
    # Run the Showcase app via WebApp runner on a free port
    app = WebApp(Showcase)
    app.run(port=port, open_browser=False)

@pytest.fixture(scope="module")
def app_port():
    port = get_free_port()
    p = multiprocessing.Process(target=run_server, args=(port,))
    p.start()
    
    # Wait for server to start
    time.sleep(2)
    
    yield port
    
    p.terminate()
    p.join()

def test_showcase_features(app_port, page: Page):
    url = f"http://127.0.0.1:{app_port}"
    page.goto(url)
    
    # 1. Reactivity
    expect(page.locator("text=Count: 0 | Items: A")).to_be_visible()
    page.click("button:has-text('+1')")
    expect(page.locator("text=Count: 1 | Items: A")).to_be_visible()
    page.click("button:has-text('Mutate')")
    expect(page.locator("text=Count: 1 | Items: A,X")).to_be_visible()

    # 2. Stepping (Yield)
    expect(page.locator("text=Ready")).to_be_visible()
    page.click("button:has-text('Start Async Process')")
    expect(page.locator("text=Step 1: Init...")).to_be_visible()
    expect(page.locator("text=Step 3: DONE!")).to_be_visible(timeout=5000)

    # 3. Binding & Class
    expect(page.locator("text=Live: Edit me")).to_be_visible()
    page.fill("input[value='Edit me']", "Hello htag")
    expect(page.locator("text=Live: Hello htag")).to_be_visible()
    
    box = page.locator("text=Live: Hello htag")
    # check that we can toggle the class
    page.click("button:has-text('Toggle State')")
    expect(box).to_have_class(re.compile(r".*active.*"))

    # 4. Tree & Dict
    page.click("button:has-text('Find & Update')")
    expect(page.locator("text=Found! Childs:")).to_be_visible()

    # 5. Events & Context
    page.on("dialog", lambda dialog: dialog.accept()) # Accept alerts
    page.click("button:has-text('UA')")
    page.click("button:has-text('Stop & Coords')")
    
    # Prevent default
    page.click("a:has-text('Prevent')")
    expect(page.locator("text=htag Showcase")).to_be_visible()

    # 6. Global Navigation Hash
    expect(page.locator("text=Hash: -")).to_be_visible()
    page.click("a:has-text('#Home')")
    expect(page.locator("text=Hash: Home")).to_be_visible()
    page.click("a:has-text('#Settings')")
    expect(page.locator("text=Hash: Settings")).to_be_visible()

    # 8. Safe Playground
    page.click("button:has-text('Add')")
    expect(page.locator("text=Target Element •")).to_be_visible()
    page.click("button:has-text('Clear')")
    expect(page.locator("text=Target Element")).not_to_be_visible()
    page.click("button:has-text('Restore')")
    expect(page.locator("text=Target Element")).to_be_visible()

    # 9. Lifecycle
    page.click("button:has-text('Mount')")
    # It prints 'Mounted: <time>'
    expect(page.locator("text=Mounted:")).to_be_visible()
    page.click("button:has-text('Unmount')")
    expect(page.locator("text=Mounted:")).not_to_be_visible()
