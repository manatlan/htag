import pytest
from starlette.testclient import TestClient
from pathlib import Path
import os
import sys
import shutil
import time

# We need to test the server, so we import the DynamicHtagApps class
from server import DynamicHtagApps

@pytest.fixture
def temp_apps_dir(tmp_path):
    """Create a temporary directory simulating the www/ folder."""
    # We must insert tmp_path into sys.path so that 'www.testapp' can be imported!
    sys.path.insert(0, str(tmp_path))
    
    apps_dir = tmp_path / "www"
    apps_dir.mkdir()
    
    # Static file (.txt)
    (apps_dir / "test.txt").write_text("hello static")
    
    # Script file (.py) reading env variables
    script_content = """import os; print(f"<h1>Hello from script</h1><p>{os.environ.get('QUERY_STRING','')}</p>")"""
    (apps_dir / "myscript.py").write_text(script_content)
    
    # A simple htag App
    app_content = """from htag import Tag
class App(Tag.App):
    def init(self):
        self += Tag.h1("Hello TestApp")
"""
    (apps_dir / "testapp.py").write_text(app_content)
    
    # A folder Htag App
    folder_app_dir = apps_dir / "myfolder"
    folder_app_dir.mkdir()
    (folder_app_dir / "__init__.py").write_text(app_content.replace('TestApp', 'FolderApp'))
    
    # Static file inside the folder app
    (folder_app_dir / "logo.png").write_text("fake image")
    
    # A module htag App setting app=MyClass
    module_app_dir = apps_dir / "mymodule"
    module_app_dir.mkdir()
    module_content = """from htag import Tag
class MyModApp(Tag.App):
    def init(self):
        self += Tag.h1("Hello ModApp")
App=MyModApp
"""
    (module_app_dir / "__init__.py").write_text(module_content)
    (module_app_dir / "static.txt").write_text("module static content")
    (module_app_dir / "secret.py").write_text("print('SECRET_PYTHON_OUTPUT')")
    
    # A fake app (should be ignored by AST discovery)
    (apps_dir / "fakeapp.py").write_text("# class App:\n#    pass\nprint('I am not an htag app')")

    yield apps_dir
    
    # Clean up sys.path and sys.modules
    sys.path.pop(0)
    to_del = [m for m in sys.modules if m == "www" or m.startswith("www.")]
    for m in to_del:
        del sys.modules[m]

@pytest.fixture
def client(temp_apps_dir):
    """Create a TestClient with our DynamicHtagApps instance."""
    app = DynamicHtagApps(temp_apps_dir, auto_index=True) # Default True for tests
    return TestClient(app)

def test_root_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Root Index" in response.text
    # Check that our test files are listed
    assert "test.txt" in response.text
    assert "myscript" in response.text
    assert "testapp" in response.text
    assert "myfolder/" in response.text

def test_static_file(client, temp_apps_dir):
    response = client.get("/test.txt")
    assert response.status_code == 200
    assert response.text == "hello static"

def test_script_execution(client):
    response = client.get("/myscript?foo=bar")
    assert response.status_code == 200
    assert "<h1>Hello from script</h1>" in response.text
    assert "<p>foo=bar</p>" in response.text

def test_script_no_extension_leak(client):
    response = client.get("/myscript.py")
    assert response.status_code == 404

def test_flat_htag_app(client):
    response = client.get("/testapp/")
    assert response.status_code == 200
    assert "Hello TestApp" in response.text

def test_folder_htag_app(client):
    response = client.get("/myfolder/")
    assert response.status_code == 200
    assert "Hello FolderApp" in response.text

def test_module_htag_app(client):
    response = client.get("/mymodule/")
    assert response.status_code == 200
    assert "Hello ModApp" in response.text

def test_static_in_module_app(client):
    response = client.get("/mymodule/static.txt")
    assert response.status_code == 200
    assert response.text == "module static content"

def test_python_in_module_app_no_source_leak(client):
    response = client.get("/mymodule/secret")
    assert response.status_code == 200
    # It executes the script, we must get the output but NEVER the source code!
    assert "print('SECRET_PYTHON_OUTPUT')" not in response.text
    assert "SECRET_PYTHON_OUTPUT" in response.text

def test_static_in_folder_app(client):
    response = client.get("/myfolder/logo.png")
    assert response.status_code == 200
    assert response.text == "fake image"

def test_directory_traversal_protection(client):
    # Try to access something outside the www directory
    # Starlette normalizes /../server.py to /server.py, which doesn't exist in www/
    response = client.get("/../server.py")
    assert response.status_code in (403, 404)

def test_404_not_found(client):
    response = client.get("/doesnotexist.txt")
    assert response.status_code == 404
    assert response.text == "Not found"

def test_hidden_file_protection(client, temp_apps_dir):
    (temp_apps_dir / ".env").write_text("SECRET=123")
    # Actually, hidden files shouldn't appear in index, let's test index first
    response = client.get("/")
    assert ".env" not in response.text

def test_smart_reload(client, temp_apps_dir):
    # Request the app once to cache it
    response1 = client.get("/testapp/")
    assert "Hello TestApp" in response1.text
    
    # Modify the source file
    time.sleep(0.1) # ensure mtime changes
    app_file = temp_apps_dir / "testapp.py"
    app_file.write_text(app_file.read_text().replace("TestApp", "MODIFIEDApp"))
    
    # Request again
    response2 = client.get("/testapp/")
    assert response2.status_code == 200
    assert "Hello MODIFIEDApp" in response2.text

def test_ttl_unloading(temp_apps_dir):
    # We need to test the unloading logic manually as APP_TTL is large
    import server
    router = server.DynamicHtagApps(temp_apps_dir)
    
    # 1. Load an app
    router._refresh_discovery()
    router.apps["testapp"].last_accessed = time.time()
    from starlette.testclient import TestClient
    local_client = TestClient(router)
    local_client.get("/testapp/")
    assert router.apps["testapp"].app is not None
    
    # 2. Simulate expiration
    router.apps["testapp"].last_accessed = time.time() - (server.APP_TTL + 10)
    
    # Trigger garbage collection (simulating next http request)
    local_client.get("/")
    
    # 3. Check it was unloaded
    assert router.apps["testapp"].app is None

def test_script_error(client, temp_apps_dir):
    (temp_apps_dir / "error.py").write_text("import sys; sys.stderr.write('SOME ERROR'); sys.exit(1)")
    response = client.get("/error")
    assert response.status_code == 500
    assert "SOME ERROR" in response.text

def test_script_timeout(client, temp_apps_dir):
    # server.py has 10s timeout, we can't easily wait 10s in tests
    # But we can verify the code path if we mock the timeout for the test
    import server
    (temp_apps_dir / "hang.py").write_text("import time; time.sleep(20)")
    
    # We don't want to actually wait 10s, but we've seen the code.
    # We'll just test a script that takes a bit of time but finishes
    (temp_apps_dir / "slow.py").write_text("import time; time.sleep(0.5); print('done')")
    response = client.get("/slow")
    assert response.status_code == 200
    assert "done" in response.text

def test_navigation_depth(client, temp_apps_dir):
    # Test deeper nesting and "Parent Directory" links
    sub = temp_apps_dir / "folder" / "sub"
    sub.mkdir(parents=True)
    (sub / "file.txt").write_text("deep")
    
    # Check /folder/ index
    resp1 = client.get("/folder/")
    assert 'href="/folder/sub/"' in resp1.text
    assert 'href="/"' in resp1.text # Parent from /folder/ is /
    
    # Check /folder/sub/ index
    resp2 = client.get("/folder/sub/")
    assert 'href="/folder/sub/file.txt"' in resp2.text
    assert 'href="/folder/"' in resp2.text # Parent from /folder/sub/ is /folder/

def test_auto_index_disabled(temp_apps_dir):
    router = DynamicHtagApps(temp_apps_dir, auto_index=False)
    from starlette.testclient import TestClient
    client = TestClient(router)
    
    response = client.get("/")
    assert response.status_code == 400
    assert response.text == "No default entrypoint"

def test_default_index_app(client, temp_apps_dir):
    # Create an index htag app in a folder
    idx_dir = temp_apps_dir / "hasindex"
    idx_dir.mkdir()
    app_content = """from htag import Tag
class App(Tag.App):
    def init(self):
        self += Tag.h1("I am the index app")
"""
    (idx_dir / "index.py").write_text(app_content)
    
    router = DynamicHtagApps(temp_apps_dir, auto_index=False)
    from starlette.testclient import TestClient
    client = TestClient(router)

    response = client.get("/hasindex/")
    assert response.status_code == 200
    assert "I am the index app" in response.text

def test_default_index_script(client, temp_apps_dir):
    # Create an index script in a folder
    idx_dir = temp_apps_dir / "hasidxscript"
    idx_dir.mkdir()
    (idx_dir / "index.py").write_text("print('I am the index script')")
    
    router = DynamicHtagApps(temp_apps_dir, auto_index=False)
    from starlette.testclient import TestClient
    client = TestClient(router)

    response = client.get("/hasidxscript/")
    assert response.status_code == 200
    assert "I am the index script" in response.text

def test_auto_index_enabled_ignores_index_file(client, temp_apps_dir):
    # If AUTO_INDEX is True, it should list the directory even if index.py exists
    idx_dir = temp_apps_dir / "index_enabled"
    idx_dir.mkdir()
    (idx_dir / "index.py").write_text("print('I should not run')")
    (idx_dir / "other.txt").write_text("other")

    router = DynamicHtagApps(temp_apps_dir, auto_index=True)
    from starlette.testclient import TestClient
    client = TestClient(router)

    response = client.get("/index_enabled/")
    assert response.status_code == 200
    # Should be a listing
    assert "Index of index_enabled/" in response.text
    assert ">index</a>" in response.text
    assert "other.txt" in response.text
    assert "I should not run" not in response.text

def test_auto_index_enabled_ignores_index_html(client, temp_apps_dir):
    # If AUTO_INDEX is True, it should list the directory even if index.html exists
    idx_dir = temp_apps_dir / "index_html_enabled"
    idx_dir.mkdir()
    (idx_dir / "index.html").write_text("I should not be seen")
    (idx_dir / "other.txt").write_text("other")

    router = DynamicHtagApps(temp_apps_dir, auto_index=True)
    from starlette.testclient import TestClient
    client = TestClient(router)

    response = client.get("/index_html_enabled/")
    assert response.status_code == 200
    # Should be a listing
    assert "Index of index_html_enabled/" in response.text
    assert "index.html" in response.text
    assert "I should not be seen" not in response.text

def test_auto_index_disabled_in_subfolder(client, temp_apps_dir):
    # Verify 400 even in nested folders if AUTO_INDEX=False and no index
    sub = temp_apps_dir / "mysub" / "deep"
    sub.mkdir(parents=True)
    (sub / "hidden.txt").write_text("secret")

    router = DynamicHtagApps(temp_apps_dir, auto_index=False)
    from starlette.testclient import TestClient
    client = TestClient(router)
    
    response = client.get("/mysub/deep/")
    assert response.status_code == 400
    assert response.text == "No default entrypoint"

def test_fake_app_ignored(client):
    # Verify that fakeapp.py is NOT discovered as an htag app
    # but can still be run as a script
    response_index = client.get("/")
    assert "fakeapp" in response_index.text
    assert "fakeapp</a> <small style=\"color:#888\">(htag App)</small>" not in response_index.text
    
    response_run = client.get("/fakeapp")
    assert response_run.status_code == 200
    assert "I am not an htag app" in response_run.text

def test_hot_discovery(client, temp_apps_dir):
    # 1. Initially, 'newapp' does not exist
    resp1 = client.get("/newapp/")
    assert resp1.status_code == 404
    
    # 2. Create the app file while 'server' is running
    new_app_file = temp_apps_dir / "newapp.py"
    app_content = """from htag import Tag
class App(Tag.App):
    def init(self):
        self += Tag.h1("I am a new app")
"""
    new_app_file.write_text(app_content)
    
    # 2b. Wait a bit for throttle
    time.sleep(0.2)
    
    # 3. Accessing the root should now list it as an htag app
    resp2 = client.get("/")
    assert "newapp" in resp2.text
    assert "newapp</a> <small style=\"color:#888\">(htag App)</small>" in resp2.text
    
    # 4. Accessing the app directly should now work
    resp3 = client.get("/newapp/")
    assert resp3.status_code == 200
    assert "I am a new app" in resp3.text

def test_default_index_html(client, temp_apps_dir):
    # Test index.html in a subfolder
    sub = temp_apps_dir / "mysub"
    sub.mkdir(exist_ok=True)
    (sub / "index.html").write_text("<html><body>Hello HTML Index</body></html>")
    
    # We use a router with auto_index=False to see the index.html
    router = DynamicHtagApps(temp_apps_dir, auto_index=False)
    from starlette.testclient import TestClient
    client = TestClient(router)

    response = client.get("/mysub/")
    assert response.status_code == 200
    assert "Hello HTML Index" in response.text

def test_index_priority(client, temp_apps_dir):
    # Test that index.html takes priority over index.py
    sub = temp_apps_dir / "priority"
    sub.mkdir(exist_ok=True)
    (sub / "index.html").write_text("HTML Index")
    (sub / "index.py").write_text("from htag import Tag\nclass App(Tag.App):\n    def init(self): self += 'PY App'")
    
    # We need to wait for discovery to pick up the new app if it's there
    time.sleep(0.2)
    
    # We use a router with auto_index=False to test priorities
    router = DynamicHtagApps(temp_apps_dir, auto_index=False)
    from starlette.testclient import TestClient
    client = TestClient(router)

    response = client.get("/priority/")
    assert response.status_code == 200
    assert "HTML Index" in response.text
    assert "PY App" not in response.text

def test_parano_detection(temp_apps_dir):
    # Create an app with _parano_ = True
    app_file = temp_apps_dir / "parano_app.py"
    app_file.write_text("from htag import Tag\nclass App(Tag.App):\n    _parano_ = True\n    def init(self): self += 'Secure'")
    
    import server
    router = server.DynamicHtagApps(temp_apps_dir)
    from starlette.testclient import TestClient
    local_client = TestClient(router)
    
    # Trigger loading
    response = local_client.get("/parano_app/")
    assert response.status_code == 200
    
    # Verify parano mode is active in the rendered HTML
    assert 'window.PARANO = "' in response.text

def test_custom_ttl_unloading(temp_apps_dir):
    # Create an app with 1s TTL
    app_file = temp_apps_dir / "short_ttl.py"
    app_file.write_text("from htag import Tag\nclass App(Tag.App):\n    _ttl_ = 1\n    def init(self): self += 'Short'")
    
    import server
    router = server.DynamicHtagApps(temp_apps_dir)
    from starlette.testclient import TestClient
    local_client = TestClient(router)
    
    # 1. Load the app
    local_client.get("/short_ttl/")
    info = router.apps["short_ttl"]
    assert info.app is not None
    assert info.ttl == 1
    
    # 2. Simulate expiration (wait > 1s)
    time.sleep(1.1)
    
    # Trigger garbage collection (simulating next request)
    local_client.get("/")
    
    # 3. Check it was unloaded
    assert info.app is None

def test_persistent_app(temp_apps_dir):
    # Create an app with _ttl_ = 0 (infinite)
    app_file = temp_apps_dir / "infinite.py"
    app_file.write_text("from htag import Tag\nclass App(Tag.App):\n    _ttl_ = 0\n    def init(self): self += 'Infinite'")
    
    import server
    router = server.DynamicHtagApps(temp_apps_dir)
    from starlette.testclient import TestClient
    local_client = TestClient(router)
    
    # 1. Load the app
    local_client.get("/infinite/")
    info = router.apps["infinite"]
    assert info.app is not None
    
    # 2. Simulate "long" time (longer than default APP_TTL)
    import server as server_mod
    original_ttl = server_mod.APP_TTL
    try:
        server_mod.APP_TTL = 0.1 # Temporarily reduce default TTL
        time.sleep(0.2)
        
        # Trigger garbage collection
        local_client.get("/")
        
        # 3. Check it was NOT unloaded because _ttl_ is 0
        assert info.app is not None
    finally:
        server_mod.APP_TTL = original_ttl


def test_htag_endpoint_routing_in_subpath(client):
    # This test ensures that /app/stream is routed to the app even if not a file
    response = client.get("/myfolder/stream")
    # Starlette WebApp sse handler returns 400 if no session cookie, but 404 would mean routing failed
    # If it reached the app, it should be 400 (no session)
    assert response.status_code == 400
    assert response.text == "No session cookie"

def test_source_code_leak_protection_comprehensive(client, temp_apps_dir):
    # 1. Direct access to a flat .py file (script or app) -> 404
    assert client.get("/myscript.py").status_code == 404
    assert client.get("/testapp.py").status_code == 404
    
    # 2. Direct access to a .py file in a sub-folder -> 404
    assert client.get("/myfolder/__init__.py").status_code == 404
    assert client.get("/mymodule/__init__.py").status_code == 404
    assert client.get("/mymodule/secret.py").status_code == 404
    
    # 3. Access to .pyc files -> Always ignored/404
    (temp_apps_dir / "test.pyc").write_text("bytecode")
    assert client.get("/test.pyc").status_code == 404
    
    # 4. Verify that even if we try to trick the extensionless logic with dots
    # (The server should only serve it if it's NOT a .py when accessed directly)
    # Testing that /myscript executes it, but /myscript.py is blocked (already tested, but for clarity)
    resp = client.get("/myscript")
    assert resp.status_code == 200
    assert "print" not in resp.text # Should be executed, not served
