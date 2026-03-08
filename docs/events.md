# Events and Reactivity

`htag` provides a seamless way to handle user interactions on the server side.

## Event Handlers

You can attach event handlers to any `Tag` component using the `_on{event}` syntax:

```python
def my_callback(e: Any) -> None:
    print(f"Clicked on {e.target.id}")
    e.target.add(Tag.span("!"))

# Attached via underscore property
btn = Tag.button("Click me", _onclick=my_callback)

# Attached via dictionary syntax
btn["onclick"] = my_callback
```

### The Event Object

The `e` argument passed to the callback is an `Event` object containing:

- `e.target`: The `Tag` instance that triggered the event.
- `e.name`: The name of the event (e.g., "click").
- Data attributes like `e.value` (for inputs), `e.x`, `e.y` (for mouse events), etc.

## Automatic Binding (Magic Bind)

`htag` automatically synchronizes the state of input elements without requiring explicit event handlers.

When you use an `<input>`, `<textarea>`, or `<select>`, `htag` injects an `_oninput` event that updates the component's `_value` attribute in real-time on the server.

```python
class MyForm(Tag.App):
    def init(self) -> None:
        # No '_oninput' needed, it's automatic!
        self.entry = Tag.input(_value="Initial")
        self <= self.entry
        self <= Tag.button("Show", _onclick=lambda e: self.add(f"Value is: {self.entry._value}"))
```

## Async Handlers

`htag` fully supports `asyncio`. You can define callbacks as `async def`:

```python
async def my_async_callback(e: Any) -> None:
    await asyncio.sleep(1)
    e.target.add("Done!")
```

## UI Streaming (Generators)

For long-running tasks that need to update the UI multiple times, you can use generators:

```python
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

```python
async def my_async_gen(e: Any) -> AsyncGenerator:
    e.target.add("Fetching...")
    yield
    await asyncio.sleep(2)
    e.target.add("Data ready!")
```

> [!TIP]
> Use generators for any operation that takes more than 100ms to keep the UI responsive and provide feedback to the user.


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

When you set `self._onhashchange`, the Python callback receives an `Event` object with `newURL` and `oldURL` attributes.

```python
class App(Tag.App):
    def init(self):
        self._onhashchange = self.on_hash
        
    def on_hash(self, e):
        print(f"Navigated to: {e.newURL}")
```

### Custom Simple Events

You can trigger custom events from JavaScript with any data using the global `htag_event` function:

```python
# In Python
tag._oncustom = lambda e: print(f"Received value: {e.value}")

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
