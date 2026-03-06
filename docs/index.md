# htag Documentation

![htag2 logo](assets/logo.png)

`htag` is a modern, state-of-the-art Python library for building interactive web applications using a declarative, component-based approach. It bridges the gap between Python and the browser by synchronizing state and events over WebSockets.

[View on GitHub](https://github.com/manatlan/htag2)

## Features

- **Component-Based**: Build complex UIs using reusable components via `Tag`.
- **Pythonic & Declarative**: Write UI logic cleanly with `with` blocks (Context Managers).
- **Reactive State**: True zero-boilerplate `State` management (like React/SolidJS) in pure Python.
- **Real-time**: Automatic synchronization of UI changes via WebSockets.
- **Responsive**: Built-in support for multiple runners (Browser, Chrome App).
- **Type-Safe**: Comprehensive type hints for a great developer experience.
- **Modern HTML**: Native support for HTML5 void elements.
- **Scoped Styles**: Simple, robust CSS scoping via the `styles` attribute.
- **Class Helpers**: Convenient methods like `toggle_class()` and `has_class()`.
- **Automatic Attributes**: Non-prefixed keyword arguments are automatically assigned as instance attributes.

## Quick Start

Creating a basic `htag` app is simple:

```python
from htag import Tag, WebApp, State


class HelloApp(Tag.App):
    def init(self) -> None:
        self.count = State(0)
        
        with Tag.div(_class="container"):
            Tag.h1("Hello htag!")
            Tag.p(lambda: f"Clicked {self.count.value} times")
            Tag.button("Click Me", _onclick=self.increment)

    def increment(self, e: Any) -> None:
        self.count.value += 1

if __name__ == "__main__":
    WebApp(HelloApp).run()
```


### Core Concepts

1.  **Tag**: The helper class to dynamically create UI components (e.g., `Tag.div()`, `Tag.input()`).
2.  **App**: A specialized tag (accessed via `Tag.App`) that acts as the root of your application and manages the server lifecycle.
3.  **Runners**: Classes like `WebApp` or `ChromeApp` that host and launch your application.

---

[Next: Components →](components.md) | [Reactivity & State →](reactivity.md)
