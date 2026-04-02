# Reactivity and State

htag features a powerful, zero-boilerplate reactivity system inspired by modern web frameworks. It allows you to build data-driven UIs where components update automatically as your data changes.

## The State Object

The `State` class is the heart of the reactivity system. It tracks dependencies and notifies components when values change.

```python
from htag import Tag, State

class MyApp(Tag.App):
    def init(self) -> None:
        self.count = State(0)
```

## The States Container (Preferred)

For managing multiple reactive variables, the `States` class is the **recommended** approach. it creates multiple `State` objects in a single container, allowing for cleaner code and bulk data operations.

```python
from htag import Tag, States

class MyApp(Tag.App):
    def init(self) -> None:
        # Initialize multiple states at once
        self.s = States(
            count=0,
            loading=False,
            user={"name": "Guest"}
        )

    def login(self, username: str):
        # Access and mutate attributes directly!
        self.s.count += 1
        self.s.user["name"] = username
```

### Bulk Save & Load

The `States` container provides two powerful methods for persistence or initialization:

- **`.dump()`**: Returns a plain dictionary mapping state names to their current values.
- **`.load(dict)`**: Updates all matching states from a dictionary.

```python
# Save current state
data = self.s.dump() # {'count': 1, 'loading': False, ...}

# Restore state
self.s.load({'count': 42}) # Triggers re-render for count observers
```

### Idempotent Constructor (Promotion)

The `State` constructor is idempotent: if you pass an existing `State` or `_StateProxy` object, it returns that object directly. This allows component developers to "promote" any input to a `State` without manually checking its type.

```python
class SubComponent(Tag.div):
    def init(self, value: Any):
        # Always safe: ensures self.v is a State object.
        # If 'value' was already a State, the original identity is preserved.
        self.v = State(value)
        self += lambda: f"Value: {self.v}"
```

### Direct Operator Usage

You can use standard Python operators directly on the `State` object. The framework automatically proxies the operation to the underlying value and triggers a re-render.

```python
Tag.button("+1", _onclick=lambda e: self.count += 1)
```

### Transparent Method Proxy & Nested Reactivity

When the state wraps a mutable object (like a list, dict, set, or tuple), calling any of its methods will automatically trigger a re-render. 

**Nested objects** are fully reactive. This includes mutations inside loops:

from typing import Any
from htag import Tag, State

self.data = State({"users": [{"name": "Alice"}, {"name": "Bob"}]})

def toggle_all(e: Any):
    # Iteration yields proxies!
    for user in self.data["users"]:
        user["name"] = user["name"].upper()
```

### Attribute & Class Delegation

`State` objects delegate attribute access and assignment to the underlying value. This allows for clean interaction with custom objects:

```python
class User:
    def __init__(self, name): self.name = name

self.user = State(User("Alice"))

# Directly assign to the state's attribute:
self.user.name = "Bob"  # Mutates User and triggers re-render!
```

### Full Operator Support

`State` objects behave like their underlying values in expressions. They support all comparison, arithmetic, and unary operators:

```python
self.count = State(10)

# Comparisons (registers dependency if used in a lambda)
if self.count > 5:
    print("Large")

# Arithmetic
new_val = self.count + 5  # 15
```

### Type Conversions

You can explicitly convert `State` objects to standard Python types:

```python
self.id_str = State("123")
id_int = int(self.id_str)

self.status = State(0)
if not self.status:  # bool() conversion
    print("Inactive")
```

### Collection Protocols

`State` objects also support standard collection protocols like indexing, length, and iteration. Accessing an element of a collection returns a proxy if it's a list or dict, maintaining reactivity:

```python
self.dico = State({"a": 1})

def update_val(e):
    self.dico["a"] = 2  # Auto-notifies!

Tag.p(lambda: f"Items: {len(self.items)}")
```

### Advanced: `.set()`, `.get()` and `.notify()`

- **`.set(new_value)`**: Updates the state and returns the new value. Useful for expressions within lambdas.
- **`.get()`**: Safely retrieves the underlying value from a `State` or `_StateProxy` object. This is essential when the wrapped value (like a `bool`) doesn't have a `.get()` method itself, and you want to dereference it safely.
- **`.notify()`**: Manually triggers observers. Useful if you've deeply mutated an object in a way that the proxy couldn't detect (though this is extremely rare with nested reactivity).

---

You can pass a `State` object directly as a child to any tag, or use a lambda for more complex expressions. htag will automatically track which `State` objects are accessed and will re-render just that part of the UI when the state changes.

```python
# Direct usage (recommended for simple values)
# htag automatically de-references s.value and registers the observer!
Tag.p(self.count)

# Lambda usage (for more complex expressions)
Tag.p(lambda: f"The current count is {self.count}")
```

### Lists of Components

Lambdas can also return lists or tuples of components. htag handles the flattening and rendering automatically.

```python
Tag.ul(lambda: [Tag.li(user.name) for user in self.users])
```

## Reactive & Boolean Attributes

Attributes (including boolean attributes like `disabled`, `checked`, etc.) can be reactive by passing a lambda OR a `State` object directly.

### Direct Attribute Reactivity

When you pass a `State` object directly as an attribute, `htag` automatically registers the tag as an observer. This is the most concise way to build reactive UIs:

```python
# No lambda needed!
Tag.button("Submit", _disabled=self.is_loading)
```

### Dynamic Classes and Styles (via Lambda)

For more complex logic, use lambdas:

```python
Tag.div(
    _class=lambda: "text-red-600" if self.error else "text-green-600",
    _style=lambda: f"opacity: {self.opacity}%"
)

# Post-instantiation, always use dictionary setter:
div["class"] = lambda: "active" if self.is_active else "hidden"
```

### Boolean Attributes

htag handles boolean attributes (like `disabled`, `checked`, `required`, `readonly`) intelligently:

- **True**: Renders the attribute name only (e.g., `<button disabled>`).
- **False / None**: Omit the attribute entirely (e.g., `<button>`).
- **Lambda / State**: Can return/contain `True`, `False`, or `None` for dynamic control.

## How it Works

1.  **Dependency Tracking**: When a reactive lambda is executed, htag records which `State` objects were read.
2.  **Notification**: When a `State` value is modified, it notifies all recorded components ("observers").
3.  **Selective Re-rendering**: The framework re-renders only the necessary components and sends the minimal HTML delta to the browser over WebSockets.
