---
name: htag2-development
description: Guidelines and best practices for building modern, state-of-the-art web applications using the htag2 framework.
---

# htag2 Developer Skill

Use this skill to design, implement, and refine web applications using the **htag2** framework.

## Core Architecture

### 1. Components (`Tag`)
Every UI element in htag2 is a component created via `Tag`.
- Use the `Tag` factory for standard HTML elements (e.g., `Tag.div`, `Tag.button`).
- Create custom components by subclassing any `Tag.*` class.
- Add children using `+=` or the `<=` operator (e.g., `self <= Tag.p("hello")` or `self += Tag.p("hello")`).
- Use the `.root` property to get a reference to the main `Tag.App` instance (useful for triggering app-level events or modals).
- Use `.parent` to access the parent component, and `.childs` to access the list of child components.
- Use `Tag.add(self, child)` or `Tag.add(lambda: ...)` for explicit addition. This is particularly useful when returning components from reactive lambdas, as it ensures they are properly parented even if they're not direct children.

```python
# -*- coding: utf-8 -*-
from htag import Tag

class MyComponent(Tag.div):
    def init(self, name: str, **kwargs: dict[str, Any]) -> None:
        # Traditional way:
        self <= Tag.h1(f"Hello {name}")
        
        # New Context Manager way (preferred for complex trees):
        with Tag.div(_class="container"):
            Tag.h2("Subtitle")
            Tag.p("Content goes here")

### 1a. Fragments (`Tag()`)
A fragment allows grouping multiple tags without rendering a wrapper tag (like `div`) in the final HTML.
- Use `Tag()` (without arguments) to create a fragment.
- **Limitation**: Since a fragment has no physical presence in the DOM, it cannot be targets of partial reactive updates. For elements that need to update their own `.text` or `_class` reactively, prefer `Tag.span()` or `Tag.div()`.

```python
with Tag() as fragment:
    Tag.span("Part 1")
    Tag.span("Part 2")
self <= fragment
```
```

### 2. Component Lifecycle
htag2 provides three lifecycle hooks to override on custom components:
- `init(**kwargs)`: Called exactly once at the end of component initialization. Use this instead of overriding `__init__` to avoid `super()` boilerplate. Positional arguments (`*args`) are automatically appended as children before `init` is evaluated.
- `on_mount()`: Fired when the component is firmly attached to the main `App` tree (`self.root` is ready).
- `on_unmount(self)`: Fired when the component is removed, ideal for cleaning up tasks, caches, or event listeners.

### 3. Composite Components
When creating complex UI components (like a Card or a Window), you should override the `add(self, o)` method so that when users do `my_card <= content`, the content goes into the correct inner container, not the root tag.

```python
class Card(Tag.div):
    def init(self, title, **kwargs):
        self._class="card"
        self <= Tag.h2(title)
        self.body = Tag.div(_class="card-body")
        # Use Tag.div.add to bypass the overridden add method during init
        Tag.div.add(self, self.body)

    def add(self, o):
        # Redirect append operations (+-) to the body container
        self.body <= o
```

### 4. State & Reactivity
htag2 supports both traditional "dirty-marking" and modern reactive `State`.

**Reactive State (Preferred for data-driven UIs)**:
- Use `from htag import State`.
- Declare state variables: `self.count = State(0)`.
- Read state dynamically using lambdas: `Tag.div(lambda: f"Count: {self.count.value}")`.
- Modify state directly: `self.count.value += 1`.
- Functional updates: Use `state.set(new_value)` if you need to update state and return the value in a single expression (e.g., inside a lambda): `_onclick=lambda e: self.count.set(self.count.value + 1)`.
- Mutable values: When mutating a value in-place (e.g., appending to a list), call `state.notify()` to force a re-render: `self.items.value.append("new"); self.items.notify()`.

**Reactive & Boolean Attributes**:
- Attributes support lambdas for dynamic updates: `Tag.div(_class=lambda: "active" if self.is_active.value else "hidden")`.
- Boolean attributes (e.g., `_disabled`, `_checked`, `_required`) are handled automatically:
    - `True`: Renders the attribute name only (e.g., `disabled`).
    - `False` or `None`: Omits the attribute entirely.

**Rapid Content Updates**:
- Use the `.text` property to quickly replace all text content of a tag: `self.my_label.text = "New Status"`. This completely clears existing children and replaces them with a single string.

**Traditional Reactivity (HTML Attributes & Events)**:
- **HTML Attributes**: MUST start with `_` (or use dictionary syntax) to be rendered as HTML attributes and trigger updates.
  - **In Tag Constructors**: `Tag.div(_class="btn", _id="myid")`
  - **Direct Assignment on `self`**: Use the underscore prefix: `self._style = "color:red"`, `self._disabled = True`.
  - **Dictionary Assignment**: You can also use dictionary syntax for attributes, perfectly handling dashes: `self["data-test"] = 123`, `self["class"] = "btn"`.
  - **Why?**: Assigning to `self.style` (without underscore) merely sets a private Python attribute that won't be rendered in HTML.
  - Correct: `_class="btn"`, `_src="image.png"`, `self["data-value"] = 5`
  - Incorrect: `class="btn"`, `src="image.png"`
- **Events**: Properties starting with `_on` (or dictionary keys starting with `on`) are mapped to Python callbacks.
  - Example: `self._onclick = my_func` or `self["onclick"] = my_func`

**CSS Class Helpers**:
- `tag.add_class("active")` — adds a class if not already present
- `tag.remove_class("active")` — removes a class if present
- `tag.toggle_class("hidden")` — adds or removes a class
- `tag.has_class("active")` — returns `bool`

### 4a. Finding Tags (`find_tag`)
You can recursively search for a tag within a tree using `self.find_tag(root, tag_id)`.
- It searches both internal htag IDs and manual HTML `id` attributes.
- Returns the `GTag` object or `None`.

```python
# In test.py example:
target = self.find_tag(self, "my-custom-id")
if target:
    target.text = "Found and updated!"
```

### 4b. Custom IDs
htag2 supports setting custom HTML IDs via `_id="myid"`.
- **Note**: To maintain reactivity with custom IDs, htag2 automatically injects a `data-htag-id` attribute. The internal communication bridge uses this to ensure partial DOM updates still target the correct element even if the HTML `id` attribute is overridden.

### 5. Forms & Inputs
htag2 automatically binds input events to Python.
- For text/number inputs, the current value is accessed safely via event handlers: `val = event.value`
- For checkboxes/toggles, the framework synchronizes the boolean state. Access it safely using `getattr(self.checkbox, "_value", False)`. Do not use `.value` directly on a checkbox component as it will raise an `AttributeError`.

### 6. Resiliency & Fallback
The `htag/server.py` implementation is fully robust against network irregularities:
- **WebSocket to HTTP Fallback**: If a WebSocket drops or fails to connect, the Javascript bridge automatically falls back to utilizing standard HTTP POST requests (`/event`) and Server-Sent Events (`/stream`).
- **Graceful Reconnections**: A user pressing F5 will not kill the server thread. The server only exits when the browser tab is explicitly closed or navigates away cleanly without returning within the 1-second reconnect window. 
- **Parano Mode (Payload Obfuscation)**: WebApp accepts a `parano=True` parameter that obfuscates all JSON traffic over WebSockets and HTTP routes. This lightweight symmetric XOR cipher hides data from simple MITM proxies without needing heavy cryptographic libraries on the frontend.

### 7. Session & Request Integration
When using `WebApp`, every tag has access to the current Starlette `Request` or `WebSocket` via the **`self.request`** property. This allows for direct access to the session, headers, and other request data.

```python
class MyComponent(Tag.div):
    def init(self):
        # Access the Starlette session directly!
        username = self.request.session.get("user", "Guest")
        self <= f"Hello {username}"

    def on_click(self, e):
        # Mutate the session
        self.request.session["last_click"] = "now"
```

### 8. Debug Mode & Error Visualization
htag2 includes a built-in visual aid mechanism to help developers track bugs:
- **`Runner(App, debug=True)` (Default)**: During development, ANY error that occurs (a Python exception in a callback, a JavaScript error, or a network disconnection) is visually reported via a Shadow DOM overlay in the screen (displaying js/traceback errors).
- **`Runner(App, debug=False)`**: Use this for production. Tracebacks are logged internally on the server, and only generic "Internal Server Error" messages are shown in the client UI to prevent sensitive data leakage.

### 9. Reactive vs Persistent Trees

When building complex hierarchical structures (like file trees or nested menus), choosing the right rendering strategy is critical for both performance and reliability.

**Dynamic (Lambda-based) Rendering**:
- **Usage**: `Tag.div(lambda: self.render_items(self.data.value))`
- **Pros**: Very clean, "standard" htag2 way.
- **Cons**: Every state change triggers a full re-render of the entire branch. In htag2, this creates **new Tag objects with new IDs**. If a user clicks an item while another update is happening, the event might be dispatched to an ID that no longer exists in the server-side tree, causing "ghost" clicks or unresponsiveness.

**Persistent (Init-based) Rendering (Recommended for complex trees)**:
- **Usage**: Build the tags once in `init()` and toggle their visibility.
- **Pros**: **Stable IDs**. Tags are created once and stay in memory. Events always reach the correct target.
- **Mechanism**: Use reactive classes to hide/show branches.

```python
def build_tree(self, folder_data):
    for item in folder_data:
        # 1. Create the toggleable branch container
        with Tag.div() as container:
            # 2. Add the header/toggle
            Tag.div(item.name, _onclick=lambda e, p=item.path: self.toggle(p))
            
            # 3. Create the children container with REACTIVE visibility
            with Tag.div(_class=lambda p=item.path: "" if p in self.expanded.value else "hidden"):
                if item.children:
                    self.build_tree(item.children) # Recurse
```

### 10. Best Practices for Large Trees

1.  **Stable IDs**: As shown above, prefer persistent tags for elements that handle clicks/inputs.
2.  **CSS Visibility over DOM Removal**: Toggling a `hidden` class is much faster than htag2's engine adding/removing elements from the DOM.
3.  **Path Normalization**: When using paths as keys in a `State(set())`, always use `os.path.normpath()` to avoid mismatching due to trailing slashes or different separators.
4.  **Closure Capture**: In loops, always use default arguments in lambdas to capture the current iteration value: `_onclick=lambda e, p=current_path: self.do(p)`.

### 11. Toast Notification System

Modern web applications should avoid blocking `alert()` boxes in favor of non-intrusive toast notifications.

**Structure**:
1.  **Container**: A fixed element (usually bottom-right) that acts as a stacking context.
2.  **Toast**: Individual components with high z-index and exit animations.

**Implementation Pattern (JS-side Timer)**:
Prefer using **client-side timers** (`setTimeout`) to trigger the auto-dismissal. This is much more efficient than using `asyncio.sleep` in Python, as it offloads the timing logic to the browser and avoids keeping Python tasks alive for simple UI effects.

```python
class App(Tag.App):
    def init(self):
        # 1. Stacking container
        self.toasts = Tag.div(_class="toast-container")
        self += self.toasts

    def notify(self, message, type="info"):
        # 2. Add individual toast with an 'expire' event
        t = Tag.div(message, _class=f"toast toast-{type}", 
                  _onexpire=lambda e: t.remove())
        self.toasts.add(t)
        
        # 3. Trigger dismissal via client-side setTimeout
        # Best Practice: Always pass an empty object {} if no DOM event is forwarded
        t.call_js(f"setTimeout(() => htag_event('{t.id}', 'expire', {{}}), 5000)")
```

**Manual JS Events (`htag_event`)**:
The global `htag_event(id, event_name, event)` function is the bridge that triggers Python callbacks from JS:
- **`id`**: The target component's ID (`self.id`).
- **`event_name`**: The callback name (e.g., `'click'`, `'expire'`).
- **`event`**: (Optional) Data object passed to the Python `event` argument. Always pass `{}` if no specific data is needed to ensure robustness across browser environments.

**Premium Aesthetics**:
Use CSS keyframes for entry animations (e.g., sliding up or fading in) and distinct background colors for Success, Error, and Info states.

### 12. Simple Events & HashChange

htag2 supports "simple events" where the `htag_event` function can be used to pass primitive values (strings, numbers) or custom objects from JavaScript to Python, bypassing the standard DOM Event extraction.

**`_onhashchange` support**:
The framework automatically handles the `hashchange` event. When `self._onhashchange` is set, the Python callback receives an `event` object with `newURL` and `oldURL` attributes.

```python
class App(Tag.App):
    def init(self):
        self._onhashchange = self.on_hash
        
    def on_hash(self, e):
        # e.newURL and e.oldURL are available
        print(f"Navigated to: {e.newURL}")
```

**Custom simple events**:
You can trigger custom events from JavaScript with any data:

```python
# In Python
tag._oncustom = lambda e: print(f"Received: {e.value}")

# In JavaScript (via call_js or statics)
htag_event('tag_id', 'custom', 'any string or number')
htag_event('tag_id', 'custom', {any: 'object'})
```

## Best Practices

### Layout & Styling
- Define CSS/JS dependencies in the `statics` class attribute on your main `App` class.
- Use modern, curated color palettes and typography.
- Prefer `Tag.style` and `Tag.script`. Remember to use `_src` for script/image URLs.

```python
# -*- coding: utf-8 -*-
class App(Tag.App):
    statics = [
        Tag.script(_src="https://cdn.tailwindcss.com"),
        Tag.style("body { background-color: #f8fafc; }")
    ]
```
### Scoped Styles
Use the `styles` class attribute for component-scoped CSS. The framework auto-prefixes every CSS rule with `.htag-ClassName` and adds it to the component's root element:

```python
class MyCard(Tag.div):
    styles = """
        .title { color: #1e40af; font-weight: bold; }
        .content { padding: 16px; border: 1px solid #e2e8f0; }
    """
    def init(self, title):
        self <= Tag.h2(title, _class="title")
        self <= Tag.p("Styles are scoped!", _class="content")
```

The generated CSS will be `.htag-MyCard .title { ... }` — no style leaking. The scoped `<style>` is injected once per class, even with multiple instances. Supports `@media` queries, `@keyframes`, pseudo-selectors (`:hover`, `::before`), and comma-separated selectors.

> **Note**: `styles` is **declarative** (class-level, processed once at init). For **dynamic** styling during interactions, use `_style`, `_class`, or class helpers:
> ```python
> self._style = "color: red;"              # inline style
> self.toggle_class("active")              # toggle CSS class
> Tag.div(_class=lambda: "on" if s.value else "off")  # reactive
> ```

### Global Statics (`Tag.statics`)
In addition to scoped styles, you can inject global dependencies or static assets (like external CSS/JS) for a specific component using the class attribute `statics`.
- `statics` must be a list of `Tag` elements (usually `Tag.script` or `Tag.style` or `Tag.link`).
- These elements are injected into the HTML `<head>` exactly once, regardless of how many instances of the component you create.
- This is useful for importing external libraries (Tailwind, Bootstrap, custom fonts, leaflet JS, etc.) required specifically by one of your components:

```python
class MapWidget(Tag.div):
    statics = [
        Tag.link(_rel="stylesheet", _href="https://unpkg.com/leaflet/dist/leaflet.css"),
        Tag.script(_src="https://unpkg.com/leaflet/dist/leaflet.js")
    ]
    
    def init(self):
        self.id = "map-container"
```

### Event Control
Use decorators to control event behavior:
- `@prevent`: Calls `event.preventDefault()` on the client side.
- `@stop`: Calls `event.stopPropagation()` on the client side.

### Use `yield` for UI Rendering (Stepping)
In event handlers, you can use `yield` to trigger partial UI updates. Combined with `async def`, this allows for clean, multi-step asynchronous progressions.

```python
async def _onclick(self, event):
    self.text = "Step 1: Processing..."
    yield # UI updates immediately to show "Processing..."

    await asyncio.sleep(1) # Asynchronous wait (non-blocking)
    self.text = "Step 2: Nearly done..."
    yield

    await asyncio.sleep(1)
    self.text = "Done!"
```

## Runner Choice & Developer Experience
- **`ChromeApp`**: Primary choice for local/desktop usage. Attempts to launch a clean desktop-like Kiosk window via Chromium/Chrome binaries. If none are found, it falls back to opening the default system browser via `webbrowser.open`.
- **Starlette Integration**: Recommended for web access. Mount your `htag_app.app` into a Starlette instance.

**Hot-Reloading for Development**:
To prevent constantly closing and re-opening your application window during development, pass `reload=True` to the runner:
```python
if __name__ == "__main__":
    from htag import ChromeApp
    # Master process watches files; child process runs server. 
    # Browser auto-reconnects and refreshes seamlessly!
    ChromeApp(MyApp).run(reload=True) 
```

## Build standalone executable
When you are in developpment using "uv" (and htag2 is installed in the venv).
Use `uv run htagm build <path>` to build a standalone executable for your htag app.

```bash
PYTHONIOENCODING="utf-8" uv run htagm build main.py
```

## Multi-Session Deployment
To ensure each user has their own isolated session/state:
- **ALWAYS** pass the `Tag.App` class to the runner, NOT an instance.

```python
if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(MyApp).run() # Correct: unique instance per user
```
