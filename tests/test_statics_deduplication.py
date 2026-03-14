from htag import Tag, App

def test_statics_deduplication_same_object():
    # A shared static object
    SHARED_JS = Tag.script("console.log('shared')")

    class Comp1(Tag.div):
        statics = [SHARED_JS]
    class Comp2(Tag.div):
        statics = [SHARED_JS]

    class MyApp(App):
        def init(self):
            self += Comp1()
            self += Comp2()

    app = MyApp()
    html = app._render_page()
    
    # Count occurrences of SHARED_JS in html
    count = html.count("console.log('shared')")
    assert count == 1, "Deduplication failed for same object"

def test_statics_deduplication_identical_content():
    # Identical but different objects
    JS1 = Tag.script("console.log('identical')")
    JS2 = Tag.script("console.log('identical')")
    
    class Comp3(Tag.div):
        statics = [JS1]
    class Comp4(Tag.div):
        statics = [JS2]
        
    app = App(Comp3(), Comp4())
    html = app._render_page()
    count = html.count("console.log('identical')")
    assert count == 1, "Deduplication failed for identical content"

def test_statics_inheritance_optimization():
    SHARED_STYLE = Tag.style("body { color: red; }")

    class Comp(Tag.div):
        statics = [SHARED_STYLE]
    
    c = Comp()
    # By default, c.statics is the same object as Comp.statics
    assert c.statics is Comp.statics

    app = App(c)
    html = app._render_page()
    count = html.count("body { color: red; }")
    assert count == 1, "Deduplication failed for class/instance shared statics"

def test_script_style_no_auto_id():
    # Verify that script and style tags don't have auto-generated IDs
    # which used to break content deduplication.
    s = Tag.script("alert(1)")
    st = Tag.style(".foo {}")
    d = Tag.div("hello")
    
    assert s.id == ""
    assert st.id == ""
    assert d.id.startswith("div-")
    
    assert 'id=""' in str(s) or 'id' not in str(s)
    assert 'id=""' in str(st) or 'id' not in str(st)
    assert f'id="{d.id}"' in str(d)

def test_statics_collection_with_mixed_types():
    # Test that collect_statics handles non-list statics gracefully
    class Comp(Tag.div):
        statics = Tag.script("console.log('single')")
    
    app = App(Comp())
    html = app._render_page()
    assert "console.log('single')" in html

def test_statics_deduplication_across_renders():
    # Verify that App.sent_statics works and prevents re-sending same statics
    SHARED = Tag.script("console.log('shared')")
    
    class MyApp(App):
        statics = [SHARED]
        def init(self):
            self.main = Tag.div()
            self += self.main

    app = MyApp()
    # Initial render: collects SHARED and puts it in sent_statics
    app._render_page()
    assert SHARED in app.sent_statics or str(SHARED) in app.sent_statics
    
    # Simulate a dynamic update adding a component with the same static (different instance/list)
    class Comp(Tag.div):
        statics = [SHARED]
    
    app.main.add(Comp())
    
    # broadcast_updates logic (manual verification)
    all_statics = []
    app.collect_statics(app, all_statics) # Should collect SHARED again
    
    # But new_statics calculation should skip it if already in sent_statics
    new_statics = [s for s in all_statics if s not in app.sent_statics]
    
    assert "console.log('shared')" not in "".join(new_statics)
