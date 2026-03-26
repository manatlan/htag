import pytest
from starlette.testclient import TestClient
from htag import Tag, WebApp

class LifecycleApp(Tag.App):
    def init(self):
        self.mounts = 0
        self.unmounts = 0
        self <= "Lifecycle"

    def on_mount(self):
        self.mounts += 1

    def on_unmount(self):
        self.unmounts += 1

class MyChild(Tag.div):
    def init(self, *args):
        self.mounts = 0
        self.unmounts = 0
    def on_mount(self):
        self.mounts += 1
    def on_unmount(self):
        self.unmounts += 1

class LifecycleAppWithChild(Tag.App):
    def init(self):
        self.child = MyChild("Child")
        self <= self.child

def test_webapp_refresh_lifecycle():
    """Verify that on_unmount is called before on_mount on page refresh (F5)."""
    webapp = WebApp(LifecycleApp)
    client = TestClient(webapp.app)
    
    # 1. First request: initial creation
    r = client.get("/")
    assert r.status_code == 200
    sid = r.cookies.get("htag_sid")
    assert sid in webapp.instances
    instance = webapp.instances[sid]
    
    assert instance.mounts == 1
    assert instance.unmounts == 0
    
    # 2. Second request: refresh (F5)
    r2 = client.get("/", cookies={"htag_sid": sid})
    assert r2.status_code == 200
    
    # On refresh, it should have unmounted once then mounted again (total 2)
    assert instance.unmounts == 1
    assert instance.mounts == 2

    # 3. Third request: refresh again
    client.get("/", cookies={"htag_sid": sid})
    assert instance.unmounts == 2
    assert instance.mounts == 3

def test_webapp_refresh_lifecycle_with_child():
    """Verify that lifecycle re-triggers recursively on page refresh."""
    webapp = WebApp(LifecycleAppWithChild)
    client = TestClient(webapp.app)
    
    r = client.get("/")
    sid = r.cookies.get("htag_sid")
    instance = webapp.instances[sid]
    child = instance.child
    
    # Initial load (htag v2 currently mounts multiple times on creation because of auto-add + root trigger)
    assert child.mounts == 3
    assert child.unmounts == 0
    
    # Page refresh
    client.get("/", cookies={"htag_sid": sid})
    
    # Recursive trigger check: should have unmounted once and mounted once more
    assert child.unmounts == 1
    assert child.mounts == 4

def test_webapp_new_session_no_unmount():
    """Verify that a brand new session only triggers mount, not unmount."""
    webapp = WebApp(LifecycleApp)
    client = TestClient(webapp.app)
    
    r = client.get("/")
    sid = r.cookies.get("htag_sid")
    instance = webapp.instances[sid]
    
    assert instance.mounts == 1
    assert instance.unmounts == 0
