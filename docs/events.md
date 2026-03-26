# Events and Interactions

`htag` provides a seamless way to handle user interactions on the server side.

## Event Handlers

You can attach event handlers to any `Tag` component using dictionary-style access (e.g., `["onclick"]`). While underscored keyword arguments like `_onclick` are still valid in **constructors**, the dictionary syntax is the standard for direct attribute management.

from typing import Any
from htag import Tag

def my_callback(e: Any) -> None:
    print(f"Clicked on {e.target.id}")
    e.target.add(Tag.span("!"))

# Attached via dictionary syntax
btn["onclick"] = my_callback

# OR in constructor
btn = Tag.button("Click me", _onclick=my_callback)
```

### The Event Object

The `e` argument passed to the callback is an `Event` object containing:

- `e.target`: The `Tag` instance that triggered the event.
- `e.name`: The name of the event (e.g., "click").
- Data attributes like `e.value` (for inputs), `e.x`, `e.y` (for mouse events), etc.

## Automatic Binding (Magic Bind)

`htag` automatically synchronizes the state of input elements without requiring explicit event handlers.

When you use an `<input>`, `<textarea>`, or `<select>`, `htag` injects an `oninput` event that updates the component's `value` attribute in real-time on the server.

```python
class MyForm(Tag.App):
    def init(self) -> None:
        # No '_oninput' needed, it's automatic!
        self.entry = Tag.input(_value="Initial")
        self <= self.entry
        self <= Tag.button("Show", _onclick=lambda e: self.add(f"Value is: {self.entry['value']}"))
```

## Form Handling (Submit)

When you use a `Tag.form`, the `submit` event (triggered by e.g. `["onsubmit"]`) receives an `Event` object where `event.value` is a dictionary containing all named form fields (`_name="fieldname"`).

You can access these fields directly on the event object using square brackets for convenience:

```python
class MyForm(Tag.form):
    def init(self) -> None:
        # Use '_name' to define the key in the form data
        self <= Tag.input(_name="user", _value="bob")
        self <= Tag.input(_name="email", _value="bob@mail.com")
        self <= Tag.input(_type="submit")
        self["onsubmit"] = self.post

    @prevent
    def post(self, e: Any) -> None:
        # e.value is {'user': '...', 'email': '...'}
        print(f"Submitting: {e['user']} ({e['email']})")
```

`htag` fully supports `asyncio`. You can define callbacks as `async def`:

import asyncio
from typing import Any

async def my_async_callback(e: Any) -> None:
    await asyncio.sleep(1)
    e.target.add("Done!")
```

## UI Streaming (Generators)

For long-running tasks that need to update the UI multiple times, you can use generators:

from typing import Any, Generator

def my_generator(e: Any) -> Generator:
    e.target.add("Starting...")
    yield # Triggers a UI update to the client
    
    import time
    time.sleep(2)
    e.target.add("Halfway...")
    yield
    
    time.sleep(2)
    e.target.add("Finished!")
```

### Async Generators

htag also supports `async for` generators for asynchronous UI streaming.

from typing import Any, AsyncGenerator

async def my_async_gen(e: Any) -> AsyncGenerator:
    e.target.add("Fetching...")
    yield
    await asyncio.sleep(2)
    e.target.add("Data ready!")
```

> [!TIP]
> Use generators for any operation that takes more than 100ms to keep the UI responsive and provide feedback to the user.


## Lifecycle Hooks

`htag` components provide three key lifecycle methods:

- **`init(**kwargs)`**: Called once when the component is created.
- **`on_mount()`**: Fired when the component is attached to the app. In `WebApp`, this is **re-triggered on every page refresh (F5)**, allowing you to reset volatile UI state (e.g., clearing status messages) while preserving the backend session instance.
- **`on_unmount()`**: Fired when the component is removed from the tree. In `WebApp`, it is **also called before every page refresh (F5)**, allowing you to properly clean up resources (e.g., cancelling background tasks) before the view is reset.

### Generators in Lifecycle Hooks
Both `on_mount` and `on_unmount` fully support `yield` (standard or async). `htag` intelligently queues `on_mount` updates until the client is ready, and ensures `on_unmount` broadcasts are sent before the component is discarded.

## Event Decorators

- `@prevent`: Calls `event.preventDefault()` in the browser.
- `@stop`: Calls `event.stopPropagation()` in the browser.

```python
from htag import prevent, stop

@prevent
def handle_submit(e):
    # Form won't reload the page
    pass
```

## Simple Events & HashChange

`htag` supports "simple events" where you can pass primitive values or custom objects from JavaScript back to Python.

### HashChange Event

When you set `self["onhashchange"]`, the Python callback receives an `Event` object with `newURL` and `oldURL` attributes.

```python
class App(Tag.App):
    def init(self):
        self["onhashchange"] = self.on_hash
        
    def on_hash(self, e):
        print(f"Navigated to: {e.newURL}")
```

### Custom Simple Events

You can trigger custom events from JavaScript with any data using the global `htag_event` function:

```python
# In Python
tag["oncustom"] = lambda e: print(f"Received value: {e.value}")

# In JavaScript
htag_event('tag_id', 'custom', 'some string')
htag_event('tag_id', 'custom', {key: 'value'})
```

If a primitive value is passed, it is available as `e.value` in Python. If an object is passed, its properties are mapped directly to the `Event` object.

## Client-side JavaScript

You can execute arbitrary JavaScript from the server using `call_js()`:

```python
class MyTag(Tag.div):
    def boom(self, e):
        self.call_js("alert('BOOM!')")
```

---

[← Components](components.md) | [Reactivity & State →](reactivity.md) | [Next: Runners →](runners.md)
