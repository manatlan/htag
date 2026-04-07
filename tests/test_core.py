from htag.core import GTag, prevent, stop, State
from htag import Tag

def test_gtag_init():
    t = Tag.div("hello")
    assert t.tag == "div"
    assert "hello" in t.childs
    assert t.id is not None
    assert t._GTag__dirty is True

def test_gtag_fallback_tag():
    # If first arg is a string and no tag defined, it becomes the tag
    t = Tag.my_custom_tag("hello")
    assert t.tag == "my-custom-tag"
    assert "hello" in t.childs
    
    # Test line 48: div fallback if no args at all
    t2 = GTag()
    assert t2.tag == "div"

def test_gtag_add_remove():
    t = Tag.div()
    child = Tag.span()
    t._GTag__dirty = False
    t.add(child)
    assert child in t.childs
    assert child.parent == t
    assert t._GTag__dirty is True
    
    t._GTag__dirty = False
    t.remove(child)
    assert child not in t.childs
    assert child.parent is None
    assert t._GTag__dirty is True

def test_gtag_clear():
    t = Tag.div("one", "two")
    t._GTag__dirty = False
    t.clear()
    assert len(t.childs) == 0
    assert t._GTag__dirty is True

    # Test clear with arguments
    t.add("one", "two")
    t._GTag__dirty = False
    t.clear("three", Tag.span("four"))
    assert len(t.childs) == 2
    assert t.childs[0] == "three"
    assert t.childs[1].tag == "span"
    assert t._GTag__dirty is True

# def test_gtag_attr_magic():
#     t = Tag.div(_class="foo", _data_id="123")
    
#     # Initialization still sets HTML attributes (via kwargs)
#     assert t["class"] == "foo"
#     assert t["data-id"] == "123"
#     assert t.id is not None
    
#     # Setting an attribute with an underscore should now just be a regular python attribute
#     t._class = "bar"
#     assert getattr(t, "_class") == "bar"
    
#     # It should not affect the HTML attribute
#     assert t["class"] == "foo"
    
#     # Regular python attribute
#     t.some_var = 42
#     assert t.some_var == 42
    
#     # Test line 96: event setter
#     def other_h(e): pass
#     t._onmouseover = other_h
#     assert "mouseover" in t._GTag__events

def test_gtag_render_attrs():
    t = Tag.div(_class="foo", _data_id="123")
    rendered = t._render_attrs()
    assert 'class="foo"' in rendered
    assert 'data-id="123"' in rendered
    assert f'id="{t.id}"' in rendered

def test_gtag_events():
    def my_handler(e): pass
    t = Tag.button(_onclick=my_handler, _onmouseover="alert(1)")
    assert "click" in t._GTag__events
    assert t._GTag__events["click"] == my_handler
    
    # Check JS literal event handling (previously missing line)
    rendered = str(t)
    assert 'onclick="htag_event' in rendered
    assert 'onmouseover="alert(1)"' in rendered

def test_tag_creator():
    MyDiv = Tag.Div
    assert MyDiv.tag == "div"
    t = MyDiv("content")
    assert isinstance(t, GTag)
    assert t.tag == "div"
    assert "Div" in Tag._registry

def test_void_elements():
    # Test input (previously a special class)
    i = Tag.Input(_value="test")
    assert i.tag == "input"
    assert str(i).startswith("<input")
    assert "/>" in str(i)
    
    # Test other void elements
    assert "/>" in str(Tag.Img(_src="foo.png"))
    assert str(Tag.Br()).startswith("<br")
    assert "/>" in str(Tag.Br())

def test_decorators():
    @prevent
    def handle_p(e): pass
    @stop
    def handle_s(e): pass
    assert handle_p._htag_prevent is True
    assert handle_s._htag_stop is True

def test_gtag_str():
    t = Tag.div("content")
    t.id = "fixme"
    assert str(t) == '<div id="fixme">content</div>'
    
    # Test line 159: fallback when tag is None
    t.tag = None
    assert str(t) == "content"

def test_gtag_list_addition():
    # Test lines 111-113 and 116-118
    t = Tag.div()
    l = [1, 2]
    res = t + l
    assert res == [t, 1, 2]
    
    res2 = l + t
    assert res2 == [1, 2, t]
    
    # Non list
    res3 = t + 3
    assert res3 == [t, 3]
    
    res4 = 4 + t
    assert res4 == [4, t]

def test_add_class():
    # Test lines 140-146
    t = Tag.div()
    t.add_class("foo")
    assert t["class"] == "foo"
    t.add_class("bar")
    assert t["class"] == "foo bar"
    t.add_class("foo") # already there
    assert t["class"] == "foo bar"

def test_remove_class():
    t = Tag.div(_class="foo bar")
    
    # Remove existing class
    class_self = t.remove_class("foo")
    assert class_self is t
    assert t["class"] == "bar"
    
    # Remove non-existing class
    t._GTag__dirty = False
    t.remove_class("baz")
    assert t["class"] == "bar"
    assert t._GTag__dirty is False # Shouldn't be marked dirty if nothing was removed
    
    # Remove last class
    t.remove_class("bar")
    assert t["class"] == ""

def test_gtag_iadd():
    t = Tag.div()
    t += "hello"
    assert "hello" in t.childs

def test_gtag_add_list():
    t = Tag.div()
    t.add(["a", "b"])
    assert "a" in t.childs
    assert "b" in t.childs

def test_gtag_call_js():
    t = Tag.div()
    t.call_js("alert(1)")
    assert "alert(1)" in t._GTag__js_calls

def test_gtag_remove_self():
    parent = Tag.div()
    child = Tag.span()
    parent.add(child)
    child.remove()
    assert child not in parent.childs
    assert child.parent is None

def test_gtag_le():
    t = Tag.div()
    t <= "hello"
    assert "hello" in t.childs
    
    child = Tag.span()
    t <= child
    assert child in t.childs
    assert child.parent == t

def test_gtag_root():
    class MyApp(Tag.App):
        pass

    app = MyApp()
    child1 = Tag.Div()
    child2 = Tag.Span()
    
    app += child1
    child1 += child2

    assert app.root is app
    assert child1.root is app
    assert child2.root is app

    # Not attached to an App
    unattached = Tag.Div()
    unattached_child = Tag.Span()
    unattached += unattached_child
    assert unattached.root is None
    assert unattached_child.root is None

def test_gtag_context_manager():
    with Tag.div() as root:
        with Tag.ul():
            Tag.li("first")
            Tag.li("second")
    
    assert root.tag == "div"
    assert len(root.childs) == 1
    ul = root.childs[0]
    assert ul.tag == "ul"
    assert len(ul.childs) == 2
    assert ul.childs[0].tag == "li"
    assert "first" in ul.childs[0].childs
    assert ul.childs[1].tag == "li"
    assert "second" in ul.childs[1].childs

def test_gtag_text_property():
    t = Tag.div("Hello", Tag.b(" World"), "!")
    # Getter should extract only the strings
    assert t.text == "Hello!"
    
    # Setter should clear and replace with a single string
    t.text = "New content"
    assert len(t.childs) == 1
    assert t.childs[0] == "New content"
    assert t.text == "New content"
    
    # Should safely convert non-strings
    t.text = 42
    assert t.text == "42"

def test_gtag_reactive_state():
    counter = State(0)
    
    t = Tag.div()
    t <= (lambda: f"Count: {counter.value}")
    
    assert str(t) == f'<div id="{t.id}">Count: 0</div>'
    
    # After rendering once, the div should be observing the state
    assert t in counter._observers
    t._GTag__dirty = False
    
    # Triggering state change
    counter.value = 1
    
    # Component should be marked dirty automatically
    assert t._GTag__dirty is True
    assert str(t) == f'<div id="{t.id}">Count: 1</div>'

def test_gtag_reparenting_and_duplicates():
    p1 = Tag.div()
    p2 = Tag.section()
    c = Tag.span()
    
    # Reparenting
    p1.add(c)
    assert c.parent == p1
    p2.add(c) # Should trigger remove() on c
    assert c.parent == p2
    assert c not in p1.childs
    
    # Duplicate add
    p2.add(c) # Should trigger removal from p2.childs before re-adding
    assert len(p2.childs) == 1
    assert p2.childs[0] == c

def test_toggle_class():
    t = Tag.div(_class="foo bar")
    
    # Toggle off existing class
    result = t.toggle_class("foo")
    assert result is t  # Returns self (chainable)
    assert t["class"] == "bar"
    
    # Toggle on missing class
    t.toggle_class("baz")
    assert t["class"] == "bar baz"
    
    # Toggle off again
    t.toggle_class("baz")
    assert t["class"] == "bar"

def test_has_class():
    t = Tag.div(_class="foo bar")
    assert t.has_class("foo") is True
    assert t.has_class("bar") is True
    assert t.has_class("baz") is False
    
    # Empty class
    t2 = Tag.div()
    assert t2.has_class("anything") is False

def test_state_notify():
    """State.notify() should mark observers dirty even without value change."""
    items = State([1, 2, 3])
    t = Tag.div()
    t <= (lambda: f"Count: {len(items.value)}")
    
    # Render to register observers
    str(t)
    assert t in items._observers
    t._GTag__dirty = False
    
    # In-place mutation + notify
    items.value.append(4)
    items.notify()
    assert t._GTag__dirty is True

def test_scoped_style_basic():
    """Basic scoped styles: class is added, CSS is prefixed."""
    class BasicScoped(GTag):
        tag = "div"
        styles = """
            .title { color: red; }
            .subtitle { font-size: 14px; }
        """

    w1 = BasicScoped()
    w2 = BasicScoped()

    # Both instances get the scope class
    assert w1.has_class("htag-BasicScoped")
    assert w2.has_class("htag-BasicScoped")

    # Statics contains scoped CSS (injected once)
    statics = getattr(BasicScoped, "statics", [])
    assert len(statics) == 1
    scoped_css = str(statics[0])
    assert ".htag-BasicScoped .title" in scoped_css
    assert ".htag-BasicScoped .subtitle" in scoped_css

def test_scoped_style_preserves_class():
    """_class from kwargs is merged with the scope class, not overwritten."""
    class PreserveClass(GTag):
        tag = "div"
        styles = ".box { margin: 0; }"

    w = PreserveClass(_class="extra custom")
    assert w.has_class("htag-PreserveClass")
    assert w.has_class("extra")
    assert w.has_class("custom")

def test_scoped_style_no_interference():
    """Components without `styles` don't get a scope class."""
    class PlainWidget(GTag):
        tag = "span"

    pw = PlainWidget()
    assert not pw.has_class("htag-PlainWidget")

def test_scoped_style_multi_selectors():
    """Comma-separated selectors each get the scope prefix."""
    class MultiSel(GTag):
        tag = "div"
        styles = ".a, .b { color: red; }"

    w = MultiSel()
    scoped_css = str(getattr(MultiSel, "statics")[-1])
    assert ".htag-MultiSel .a" in scoped_css
    assert ".htag-MultiSel .b" in scoped_css

def test_scoped_style_pseudo_selectors():
    """Pseudo-classes and pseudo-elements are preserved."""
    class PseudoSel(GTag):
        tag = "div"
        styles = """
            .btn:hover { color: blue; }
            .icon::before { content: ""; }
            .link:not(.disabled) { cursor: pointer; }
        """

    w = PseudoSel()
    scoped_css = str(getattr(PseudoSel, "statics")[-1])
    assert ".htag-PseudoSel .btn:hover" in scoped_css
    assert ".htag-PseudoSel .icon::before" in scoped_css
    assert ".htag-PseudoSel .link:not(.disabled)" in scoped_css

def test_scoped_style_media_query():
    """@media rules are preserved, inner selectors are scoped."""
    class MediaQ(GTag):
        tag = "div"
        styles = """
            .title { color: red; }
            @media (max-width: 768px) {
                .title { font-size: 14px; }
                .subtitle, .note { display: none; }
            }
        """

    w = MediaQ()
    scoped_css = str(getattr(MediaQ, "statics")[-1])
    # Outer rule scoped
    assert ".htag-MediaQ .title" in scoped_css
    # @media preserved
    assert "@media (max-width: 768px)" in scoped_css
    # Inner rules inside @media also scoped
    assert ".htag-MediaQ .subtitle" in scoped_css
    assert ".htag-MediaQ .note" in scoped_css

def test_scoped_style_keyframes_passthrough():
    """@keyframes are passed through without scoping internal selectors."""
    class WithKeyframes(GTag):
        tag = "div"
        styles = """
            .spinner { animation: spin 1s linear infinite; }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        """

    w = WithKeyframes()
    scoped_css = str(getattr(WithKeyframes, "statics")[-1])
    # Normal rule scoped
    assert ".htag-WithKeyframes .spinner" in scoped_css
    # @keyframes preserved unchanged
    assert "@keyframes spin" in scoped_css
    assert "0%" in scoped_css
    assert "100%" in scoped_css
    # 0% and 100% should NOT be prefixed
    assert ".htag-WithKeyframes 0%" not in scoped_css
    assert ".htag-WithKeyframes 100%" not in scoped_css

def test_scoped_style_nested_selectors():
    """Descendant and child combinators are handled correctly."""
    class NestedSel(GTag):
        tag = "div"
        styles = """
            .card .title { color: red; }
            .card > .body { padding: 10px; }
            .list .item .name { font-weight: bold; }
        """

    w = NestedSel()
    scoped_css = str(getattr(NestedSel, "statics")[-1])
    assert ".htag-NestedSel .card .title" in scoped_css
    assert ".htag-NestedSel .card > .body" in scoped_css
    assert ".htag-NestedSel .list .item .name" in scoped_css

def test_scoped_style_nested_components():
    """Nested components each get their own independent scope."""
    class Outer(GTag):
        tag = "div"
        styles = ".header { color: blue; }"

    class Inner(GTag):
        tag = "span"
        styles = ".header { color: red; }"

    outer = Outer()
    inner = Inner()
    outer.add(inner)

    # Each has its own scope class
    assert outer.has_class("htag-Outer")
    assert not outer.has_class("htag-Inner")
    assert inner.has_class("htag-Inner")
    assert not inner.has_class("htag-Outer")

    # Statics are independent
    outer_css = str(getattr(Outer, "statics")[-1])
    inner_css = str(getattr(Inner, "statics")[-1])
    assert ".htag-Outer .header" in outer_css
    assert ".htag-Inner .header" in inner_css
    assert ".htag-Inner" not in outer_css
    assert ".htag-Outer" not in inner_css

def test_scoped_style_dynamic_add():
    """Dynamically created and added scoped components work correctly."""
    class DynComp(GTag):
        tag = "div"
        styles = ".label { font-size: 12px; }"

    parent = Tag.section()

    # Dynamically create and add multiple instances
    for i in range(5):
        child = DynComp(_class=f"item-{i}")
        parent.add(child)

    assert len(parent.childs) == 5
    for child in parent.childs:
        assert child.has_class("htag-DynComp")

    # Statics injected only once regardless of instance count
    assert len(getattr(DynComp, "statics")) == 1

def test_scoped_style_with_existing_statics():
    """Scoped styles coexist with class-level statics."""
    class WithStatics(GTag):
        tag = "div"
        statics = [Tag.link(_rel="stylesheet", _href="app.css")]
        styles = ".content { padding: 8px; }"

    w = WithStatics()
    statics = getattr(WithStatics, "statics")
    # Original static + scoped style
    assert len(statics) == 2
    assert "app.css" in str(statics[0])
    assert ".htag-WithStatics .content" in str(statics[1])

def test_scoped_style_complex_css():
    """Full integration with complex real-world CSS."""
    class ComplexWidget(GTag):
        tag = "div"
        styles = """
            .card { background: white; border-radius: 8px; }
            .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
            .header, .footer { padding: 16px; border-bottom: 1px solid #eee; }
            .body > .row { display: flex; gap: 8px; }
            .body > .row:nth-child(odd) { background: #f9f9f9; }
            @media (max-width: 640px) {
                .body > .row { flex-direction: column; }
                .header, .footer { padding: 8px; }
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .card { animation: fadeIn 0.3s ease-in; }
        """

    w = ComplexWidget()
    css = str(getattr(ComplexWidget, "statics")[-1])

    # Normal selectors scoped
    assert ".htag-ComplexWidget .card" in css
    assert ".htag-ComplexWidget .card:hover" in css
    assert ".htag-ComplexWidget .header" in css
    assert ".htag-ComplexWidget .footer" in css
    assert ".htag-ComplexWidget .body > .row" in css
    assert ".htag-ComplexWidget .body > .row:nth-child(odd)" in css

    # @media preserved, inner rules scoped
    assert "@media (max-width: 640px)" in css
    # Inner should be scoped too
    assert ".htag-ComplexWidget .body > .row" in css

    # @keyframes preserved unchanged
    assert "@keyframes fadeIn" in css
    assert ".htag-ComplexWidget from" not in css
    assert ".htag-ComplexWidget to" not in css

def test_gtag_dict_attr_access():
    t = Tag.div(_class="foo", _data_id="123")
    
    # __getitem__
    assert t["class"] == "foo"
    assert t["data-id"] == "123"
    
    # __setitem__
    t["data-state"] = "active"
    assert t._GTag__attrs["data-state"] == "active"
    
    # __delitem__
    del t["class"]
    assert "class" not in t._GTag__attrs
    
def test_gtag_dict_event_access():
    def h1(e): pass
    def h2(e): pass
    
    t = Tag.button(_onclick=h1)
    
    # __getitem__
    assert t["onclick"] == h1
    
    # __setitem__
    t["onmouseover"] = h2
    assert t._GTag__events["mouseover"] == h2
    
    # __delitem__
    del t["onclick"]
    assert "click" not in t._GTag__events

def test_gtag_auto_attr_assignment():
    """Test that non-prefixed kwargs are assigned as instance attributes."""
    t = Tag.div("hello", toto=42, name="test")
    assert t.toto == 42
    assert t.name == "test"
    # Ensure they are NOT in HTML attributes
    assert "toto" not in t._get_attrs()
    assert "name" not in t._get_attrs()

    # Test collision with GTag properties
    t2 = Tag.div(tag="overridden")
    assert t2.tag == "overridden"

    # Test that subclasses can use these attributes in init()
    class MyTag(Tag.div):
        def init(self, **kwargs):
            self.success = (self.val == 123)
    
    t3 = MyTag(val=123)
    assert t3.val == 123
    assert t3.success is True

def test_state_direct_usage():
    """State objects can be used directly as children and are reactive."""
    s = State(0)
    t = Tag.div(s)
    
    # Initial render should show value
    assert str(t) == f'<div id="{t.id}">0</div>'
    
    # Tag should be observing the state
    assert t in s._observers
    t._GTag__dirty = False
    
    # Update state
    s.value = 1
    assert t._GTag__dirty is True
    assert str(t) == f'<div id="{t.id}">1</div>'

def test_state_repr_str():
    """State objects have proper repr and str (showing their value)."""
    s = State(42)
    assert str(s) == "42"
    assert repr(s) == "42"
    
    s2 = State("hello")
    assert str(s2) == "hello"
    assert repr(s2) == "'hello'"

def test_state_inplace_operators():
    s = State(10)
    s += 5; assert s.value == 15
    s -= 5; assert s.value == 10
    s *= 2; assert s.value == 20
    s /= 2; assert s.value == 10.0
    s //= 3; assert s.value == 3.0
    s %= 2; assert s.value == 1.0
    s **= 2; assert s.value == 1.0
    
    s = State(1)
    s <<= 1; assert s.value == 2
    s >>= 1; assert s.value == 1
    s &= 1; assert s.value == 1
    s ^= 0; assert s.value == 1
    s |= 2; assert s.value == 3

def test_state_fallback_setattr():
    class Dummy: pass
    d = Dummy()
    s = State(d)
    s.foo = "bar"
    assert d.foo == "bar"
    
    # Coverage for line 73: AttributeError fallback
    s2 = State(42) # int doesn't have __dict__ generally
    s2.not_an_attr = "val"
    assert s2.not_an_attr == "val"

def test_state_proxy_advanced():
    s = State([1, 2])
    proxy = s[0] # Not actually a proxy for an int, it wraps the container
    
    # Test with a dict
    s = State({"a": 1})
    proxy = s._wrap(s.value)
    
    # getattr / setattr / delattr on proxy
    class Obj:
        def method(self): return 42
    o = Obj()
    s_obj = State(o)
    proxy_obj = s_obj._wrap(o)
    assert proxy_obj.method() == 42
    
    proxy_obj.x = 10
    assert o.x == 10
    del proxy_obj.x
    assert not hasattr(o, "x")
    
    # __delitem__ / __len__ / __iter__ / __contains__
    s_list = State([10, 20])
    p_list = s_list._wrap(s_list.value)
    del p_list[0]
    assert p_list() == [20]
    assert len(p_list) == 1
    assert list(iter(p_list)) == [20]
    assert 20 in p_list
    
    # operators
    assert p_list == [20]
    assert p_list < [30]
    assert p_list + [30] == [20, 30]
    
    # __call__ observer reg
    t = Tag.div()
    from htag.core import _ctx
    _ctx.current_eval = t
    p_list()
    assert t in s_list._observers
    _ctx.current_eval = None

def test_gtag_edge_cases():
    # Tag(None) -> fragment
    t = GTag(None, "content")
    assert t.tag is None
    assert str(t) == "content"
    
    # statics as single object + styles to trigger list conversion in __init__
    class StaticTag(GTag):
        statics = Tag.style(".foo{}")
        styles = ".bar {color:red}"
    st = StaticTag()
    # Now statics is the list [original_static, scoped_static]
    all_statics = getattr(StaticTag, "statics")
    assert isinstance(all_statics, list)
    assert any(".foo{}" in str(s) for s in all_statics)
    
    # add(None)
    t.add(None)
    assert len(t.childs) == 1 # still just "content"
    
    # __getattr__ missing
    try:
        t.non_existent
    except AttributeError:
        pass
    
    # __getitem__ TypeError
    try:
        t[0]
    except TypeError:
        pass

    # __delitem__ KeyError
    try:
        del t["missing"]
    except KeyError:
        pass

def test_gtag_reactive_lifecycle():
    # Test that components inside lambdas trigger lifecycle
    c = Tag.span()
    mounted = False
    def on_m(): nonlocal mounted; mounted = True
    c.on_mount = on_m
    
    app = Tag.App()
    t = Tag.div(lambda: c)
    app.add(t)
    
    # Trigger render
    str(app)
    assert c.root is app
    assert mounted is True

def test_gtag_reactive_list_none():
    t = Tag.div(lambda: [Tag.b("1"), Tag.i("2")])
    rendered = str(t)
    assert "<b" in rendered
    assert ">1</b>" in rendered
    assert "<i" in rendered
    assert ">2</i>" in rendered
    
    t2 = Tag.div(lambda: None)
    assert str(t2).strip().endswith("></div>")

def test_decorators_bound_methods():
    class T:
        def my_method(self): pass
    t = T()
    cb_p = prevent(t.my_method)
    cb_s = stop(t.my_method)
    assert cb_p._htag_prevent is True
    assert cb_s._htag_stop is True
    # Verify they are callable
    assert callable(cb_p)
    assert callable(cb_s)
    # Check that it works (wrapper calls original)
    called = False
    def my_handler(): nonlocal called; called = True
    cb = prevent(my_handler)
    cb()
    assert called is True
