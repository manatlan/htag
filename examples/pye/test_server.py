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
class app(Tag.App):
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
app=MyModApp
"""
    (module_app_dir / "__init__.py").write_text(module_content)
    (module_app_dir / "static.txt").write_text("module static content")
    (module_app_dir / "secret.py").write_text("print('SECRET_PYTHON_OUTPUT')")

    yield apps_dir
    
    # Clean up sys.path
    sys.path.pop(0)

@pytest.fixture
def client(temp_apps_dir):
    """Create a TestClient with our DynamicHtagApps instance."""
    app = DynamicHtagApps(temp_apps_dir)
    return TestClient(app)

def test_root_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Root Index" in response.text
    # Check that our test files are listed
    assert "test.txt" in response.text
    assert "myscript.py" in response.text
    assert "testapp" in response.text
    assert "myfolder/" in response.text

def test_static_file(client, temp_apps_dir):
    response = client.get("/test.txt")
    assert response.status_code == 200
    assert response.text == "hello static"

def test_script_execution(client):
    response = client.get("/myscript.py?foo=bar")
    assert response.status_code == 200
    assert "<h1>Hello from script</h1>" in response.text
    assert "<p>foo=bar</p>" in response.text

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
    response = client.get("/mymodule/secret.py")
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
    assert response.text == "App or file not found"

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

