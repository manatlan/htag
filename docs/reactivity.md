# Reactivity and State

htag2 features a powerful, zero-boilerplate reactivity system inspired by modern web frameworks. It allows you to build data-driven UIs where components update automatically as your data changes.

## The State Object

The `State` class is the heart of the reactivity system. It tracks dependencies and notifies components when values change.

```python
from htag import Tag, State

class MyApp(Tag.App):
    def init(self) -> None:
        self.count = State(0)
```

### Direct Operator Usage

You can use standard Python operators directly on the `State` object. The framework automatically proxies the operation to the underlying value and triggers a re-render.

```python
Tag.button("+1", _onclick=lambda e: self.count += 1)
```

### Transparent Method Proxy

When the state wraps a mutable object (like a list or dict), calling any of its methods (e.g., `.append()`, `.update()`, `.pop()`) will automatically trigger a re-render after the method executes.

```python
self.items = State(["a", "b"])

def add_item(e):
    self.items.append("c")  # Automatically triggers re-render!
```

### Collection Protocols

`State` objects also support standard collection protocols like indexing, length, and iteration:

```python
self.dico = State({"a": 1})

def update_val(e):
    self.dico["a"] = 2  # Auto-notifies!

Tag.p(lambda: f"Items: {len(self.items)}")
```

### Advanced: `.set()` and `.notify()`

- **`.set(new_value)`**: Updates the state and returns the new value. Useful for expressions within lambdas.
- **`.notify()`**: Manually triggers observers. Useful if you've deeply mutated an object in a way that the proxy couldn't detect (though this is rare).

---

You can pass a `State` object directly as a child to any tag, or use a lambda for more complex expressions. htag2 will automatically track which `State` objects are accessed and will re-render just that part of the UI when the state changes.

```python
# Direct usage (recommended for simple values)
Tag.p(self.count)

# Lambda usage (for expressions)
Tag.p(lambda: f"The current count is {self.count}")
```

### Lists of Components

Lambdas can also return lists or tuples of components. htag2 handles the flattening and rendering automatically.

```python
Tag.ul(lambda: [Tag.li(user.name) for user in self.users])
```

## Reactive & Boolean Attributes

Attributes can also be reactive by passing a lambda.

### Dynamic Classes and Styles

```python
    _class=lambda: "text-red-600" if self.error else "text-green-600",
    _style=lambda: f"opacity: {self.opacity}%"
)

# Also works with dictionary syntax
div["class"] = lambda: "active" if self.is_active else "hidden"
```

### Boolean Attributes

htag2 handles boolean attributes (like `disabled`, `checked`, `required`, `readonly`) intelligently:

- **True**: Renders the attribute name only (e.g., `<button disabled>`).
- **False / None**: Omit the attribute entirely (e.g., `<button>`).
- **Lambda**: Can return `True`, `False`, or `None` for dynamic control.

```python
Tag.button("Submit", _disabled=lambda: self.is_loading)
```

## How it Works

1.  **Dependency Tracking**: When a reactive lambda is executed, htag2 records which `State` objects were read.
2.  **Notification**: When a `State` value is modified, it notifies all recorded components ("observers").
3.  **Selective Re-rendering**: The framework re-renders only the necessary components and sends the minimal HTML delta to the browser over WebSockets.
