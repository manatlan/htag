from htag.core import GTag
from htag import Tag

def test_gtag_init_called():
    class MyTag(GTag):
        def init(self):
            self.init_called = True
            self.test_val = 42

    t = MyTag("div")
    assert getattr(t, "init_called", False) is True
    assert t.test_val == 42

def test_gtag_on_mount_unmount_app():
    class MyChild(GTag):
        def init(self):
            self.mounts = 0
            self.unmounts = 0
        def on_mount(self):
            self.mounts += 1
        def on_unmount(self):
            self.unmounts += 1

    class MyApp(Tag.App):
        pass

    app = MyApp()
    child = MyChild("div")
    
    assert child.mounts == 0
    assert child.unmounts == 0
    
    # Adding to app should trigger mount
    app += child
    assert child.mounts == 1
    assert child.unmounts == 0
    
    # Removing from app should trigger unmount
    app.remove(child)
    assert child.mounts == 1
    assert child.unmounts == 1

    # Adding a nested structure to the app
    parent_tag = Tag.div()
    parent_tag += child
    assert child.mounts == 1 # still 1 because parent isn't in tree yet
    assert child.unmounts == 1
    
    app += parent_tag
    assert child.mounts == 2 # now it's in the tree
    
    app.clear()
    assert child.mounts == 2
    assert child.unmounts == 2
