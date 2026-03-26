# Components

Components are the building blocks of an `htag` application. Every visual element is a `Tag` or a subclass of it.

## Tag.div

`Tag.div` is the core class (the generic component). It handles HTML rendering, state management, and lifecycle.

### Creating a Component

You can create a custom component by subclassing `Tag.div`, for example:

```python
from htag import Tag

class MyComponent(Tag.div):
    def init(self, name: str) -> None:
        self["class"] = "my-class"
        self.add(f"Hello {name}!")
```

### Automatic Attribute Assignment

Any non-prefixed keyword argument (not starting with `_` or `_on`) passed during component instantiation is automatically assigned as an instance attribute *before* the `init()` hook is called.

**Important**: Post-instantiation, you MUST use dictionary syntax (e.g., `self["class"] = "foo"`) to set HTML attributes instead of the legacy `self._class = "foo"`.

```python
class MyTag(Tag.div):
    def init(self, **kwargs):
        # self.v is already 42!
        self <= f"Value is {self.v}"

t = MyTag(v=42)
```


### Lifecycle Hooks

Lifecycle hooks let you run code at specific times in a component's life:

- `init(*args, **kwargs)`: Called exactly once at the end of component initialization. Use this instead of overriding `__init__` to avoid `super()` boilerplates.
- `on_mount()`: Called when the component is attached to the application DOM tree. Use this for subscribing to events or initializing resources that need a live DOM. Good for subscribing to events or doing initial fetches.
- `on_unmount(self)`: Called when the component (or its parent) is removed from the `Tag.App`. Good for cleaning up tasks or event listeners.

> [!TIP]
> Both `on_mount()` and `on_unmount()` fully support the `yield` keyword (or `yield` in `async` generators) for **progressive UI rendering**. Just like in event handlers, you can yield intermediate states (e.g., "Loading..."), and `htag` will safely queue and display them to the user. For `on_unmount`, remember to store an eager reference to your targets (like `self.app_root = self.root` in `init`), because by the time the generator runs, the component is already detached from the tree.

```python
class Clock(Tag.div):
    def init(self) -> None:
        self["class"] = "clock"
        self.taskId: int | None = None
        
    def on_mount(self) -> None:
        # We are on the screen! Start ticking...
        print("Clock mounted")
        
    def on_unmount(self) -> None:
        # We are removed from the screen! Cleanup...
        print("Clock unmounted")

### Background Tasks & `update()`

- **Automatic Reactivity**: `State` mutations from background tasks (started via `asyncio.create_task`) now automatically trigger UI updates.
- **Manual Synchronization**: For non-state changes, use `self.update()` to schedule a throttled UI sync.

```python
    def on_mount(self):
        async def run():
            while True:
                self.count += 1
                await asyncio.sleep(1)
        self.task = asyncio.create_task(run())
```

### Tree Manipulation

- `self.add(*content)`: Adds children (strings or other components).
- `self <= content`: An elegant shorthand for `self.add(content)`.
- `self.remove(child)`: Removes a child component or string.
- `self.remove()`: Removes the component itself from its parent (equivalent to the old `remove_self()`).
- `self.clear(*content)`: Removes all children and optionally adds new content.
- `self.root`: Returns the `Tag.App` instance this component belongs to (or `None` if unattached).
- `self.parent`: Returns the parent `GTag` instance (or `None` if unattached).
- `self.childs`: A list of the component's children (strings or other `GTag` instances).

```python
# Using the <= operator
row = Tag.div()
row <= Tag.span("Left")
row <= Tag.span("Right")
```

### Declarative UI (Context Managers)

The preferred way to build complex component trees is using the `with` statement. New tags created inside a `with` block are automatically appended to the parent tag.

```python
with Tag.div(_class="card"):
    Tag.h2("Title")
    with Tag.div(_class="content"):
        Tag.p("This is automatically added to the content div.")
```

### Rapid Content Replacement (`.text`)

Use the `.text` property to quickly replace all children of a tag with a single string. This is more efficient for simple text updates.

```python
self.label.text = "Status: OK"
```

Attributes can be managed in two ways: using underscore-prefixed keyword arguments during **instantiation**, or using **dictionary-style access** on any `Tag` instance. The dictionary access is the preferred way for dynamic property management as it handles all HTML attributes (including those with dashes) and triggers UI updates.

### In Constructors
Ideal for quick definitions during tag creation.

```python
# In constructors
img = Tag.img(_src="/logo.png", _alt="Logo")
```

### Dictionary Access
Recommended for all dynamic property management, especially for attributes with dashes (like `data-*` or `aria-*`). **Note: internal underscores are automatically converted to dashes.**

```python
# Canonical way for dashed attributes
div["data-user-id"] = "123"

# Also perfectly valid (dashes are handle by the dict key)
div["style"] = "color: red"

# Dynamic access
attr_name = "class"
div[attr_name] = "active"
```

- `["class"]`: Maps to the `class` attribute.
- `["id"]`: Maps to the `id` attribute.
- `["style"]`: Maps to the `style` attribute.
- `["any-thing"]`: Maps to `any-thing` in HTML.

### CSS Class Helpers

Convenience methods for manipulating CSS classes:

```python
tag.add_class("active")       # add if not present
tag.remove_class("active")    # remove if present
tag.toggle_class("hidden")    # add or remove
tag.has_class("active")       # returns bool
```

All mutating methods return `self` for chaining and only mark the component dirty if the class list actually changed.

## Scoped Styles

Use the `styles` class attribute to define CSS that is automatically scoped to the component:

```python
class MyCard(Tag.div):
    styles = """
        .title { color: #1e40af; font-weight: bold; }
        .content { padding: 16px; border: 1px solid #e2e8f0; }
    """
    def init(self, title):
        self <= Tag.h2(title, _class="title")
        self <= Tag.p("No style leaking!", _class="content")
```

The framework generates scoped selectors (e.g., `.htag-MyCard .title`) and automatically adds the `htag-MyCard` class to the root element **after** the `init()` call, ensuring it's not accidentally overwritten.

Every rule in `styles` is transformed to match both the element itself and its descendants. For example, `.title` becomes `.htag-MyCard.title, .htag-MyCard .title`. It also handles tag selectors correctly (e.g., `div` becomes `div.htag-MyCard, .htag-MyCard div`).

Supported CSS features:
- `@media` (inner rules are recursively scoped)
- `@keyframes` (passed through unchanged to avoid breaking animations)
- Pseudo-selectors (`:hover`, `::before`, `:nth-child`, etc.)
- Comma-separated selectors and all combinators (`>`, `+`, `~`, spaces)

> [!NOTE]
> `styles` is **declarative** (processed once at class level). For dynamic styling during interactions, use dictionary syntax (e.g., `self["style"] = "..."`) or `toggle_class()`.

---

## The Tag Creator

The `Tag` singleton allows you to create standard HTML elements dynamically using a clean syntax:

```python
from htag import Tag

# Equivalent to <div class="foo">content</div>
d = Tag.div("content", _class="foo")

# Equivalent to <br/> (Void Element)
b = Tag.br()

# Equivalent to <input type="text" name="user" value="hello"/>
# Use '_name' to correctly populate form data in 'submit' events
i = Tag.input(_type="text", _name="user", _value="hello")
```

### Void Elements

`htag` automatically handles HTML void elements (self-closing tags) like `input`, `img`, `br`, `hr`, etc. You don't need to specify a closing tag for these.

---

[← Home](index.md) | [Next: Events →](events.md)
