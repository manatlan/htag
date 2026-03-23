import pytest
import multiprocessing
import time
import socket
from playwright.sync_api import Page, expect

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def run_server(port):
    from htag import Tag, WebApp

    class MyApp(Tag.App):
        def init(self):
            self += Tag.button("Early Action", _onclick=self.early_action, id="btn")
            self += Tag.div("0", id="status")

        def early_action(self, e):
            self.childs[1].text = str(int(self.childs[1].text) + 1)

    app = WebApp(MyApp)
    app.run(port=port, open_browser=False)

@pytest.fixture(scope="module")
def app_port():
    port = get_free_port()
    p = multiprocessing.Process(target=run_server, args=(port,))
    p.start()
    time.sleep(2)
    yield port
    p.kill()
    p.join(timeout=1)


def test_ws_early_queue(app_port, page: Page):
    url = f"http://127.0.0.1:{app_port}"
    page.goto(url)
    
    # Wait for htag initialized
    page.locator("#status").wait_for(state="attached")

    # We evaluate a precise JS test to verify the queue logic introduced in client_js.py
    js_test = """
        () => {
            // Ensure queue exists
            window._htag_queue = [];
            
            var payload1 = {id: 'btn', event: 'onclick', data: {callback_id: 'mock1'}};
            var payload2 = {id: 'btn', event: 'onclick', data: {callback_id: 'mock2'}};
            
            // 1) Force WebSocket into CONNECTING state (0)
            var original_ws = window.ws;
            var mock_ws = {
                readyState: 0, 
                sent: [],
                send: function(data) { this.sent.push(data); },
                onopen: original_ws.onopen
            };
            
            // Temporarily replace ws
            window.ws = mock_ws;
            
            // Call transport
            window.htag_transport(payload1);
            window.htag_transport(payload2);
            
            // Verify items are queued
            if (window._htag_queue.length !== 2) {
                return "FAIL: Queue length is " + window._htag_queue.length;
            }
            
            // 2) Trigger onopen
            window.ws.onopen();
            
            // Verify items are sent and queue is emptied
            if (window._htag_queue.length !== 0) {
                return "FAIL: Queue not emptied, length is " + window._htag_queue.length;
            }
            if (mock_ws.sent.length !== 2) {
                return "FAIL: Items not sent, sent length is " + mock_ws.sent.length;
            }
            
            // Restore original
            window.ws = original_ws;
            return "SUCCESS";
        }
    """
    
    result = page.evaluate(js_test)
    assert result == "SUCCESS"

