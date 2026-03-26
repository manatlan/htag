---
name: htag-development
description: Guidelines and best practices for building modern, state-of-the-art web applications using the htag v2 framework.
---

# htag Developer Skill

Use this skill to design, implement, and refine web applications using the **htag** framework.

## Core Architecture

### 1. Components (`Tag`)
Every UI element in htag is a component created via `Tag`.
- Use the `Tag` factory for standard HTML elements (e.g., `Tag.div`, `Tag.button`).
- Create custom components by subclassing any `Tag.*` class.
- Add children using `+=` or the `<=` operator (e.g., `self <= Tag.p("hello")` or `self += Tag.p("hello")`).
- Use the `.root` property to get a reference to the main `Tag.App` instance (useful for triggering app-level events or modals).
- Use `.parent` to access the parent component, and `.childs` to access the list of child components.
- Use `Tag.add(self, child)` or `Tag.add(lambda: ...)` for explicit addition. This is particularly useful when returning components from reactive lambdas, as it ensures they are properly parented even if they're not direct children.
- Use `self.clear(*content)` to remove all children and optionally add new content in one call.

**XSS Protection**: All strings added as children (e.g. `Tag.div("hello")`) are automatically HTML-escaped to prevent XSS (except for `style` and `script` tags).


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
htag provides three lifecycle hooks to override on custom components:
- `init(**kwargs)`: Called exactly once at the end of component initialization. Use this instead of overriding `__init__` to avoid `super()` boilerplate. 
    - **Automatic Assignment**: Any non-prefixed keyword argument (not starting with `_` or `_on`) is automatically assigned as an instance attribute *before* `init` is called.
    - **Example**: `Tag.div(toto=42)` will result in the instance having a `.toto` attribute set to `42`.
    - **Positional Arguments**: `*args` are automatically appended as children before `init` is evaluated.
- `on_mount()`: Fired when the component is firmly attached to the main `App` tree (`self.root` is ready).
    - **F5 / Page Load**: In `WebApp`, `on_mount()` is re-triggered on every initial page load (`GET /`), even if the session instance is reused. This allows components to reset ephemeral UI state (like status labels or timers) whenever the user refreshes the page.
- `on_unmount(self)`: Fired when the component is removed from the tree. In `WebApp`, it is **also called before every page refresh (F5)**, allowing you to properly clean up resources (e.g., cancelling background tasks) before the view is reset.

> [!NOTE]
> **Multiple Mounts version Init**: You might notice `on_mount` called multiple times during the initial load if you use both `GTag`'s auto-stack mechanism and manual addition (e.g., `self.child = MyChild(); self <= self.child`). This is harmless but good to know when counting mounts in tests.

> **Progressive UI note**: Both `on_mount()` and `on_unmount()` support `yield` (or `yield` in `async` generators) for progressive, multi-step UI rendering. In `WebApp`, `on_unmount()` is correctly called before `on_mount()` version a page refresh (F5), ensuring resource cleanup (e.g. cancelling tasks). `htag` intelligently queues `on_mount` generators until the client connects. *Remember for `on_unmount`: store a reference to external targets before returning the generator (e.g., `self.app_root = self.root`), as the component is detached and `self.parent` relies on `None` when the generator executes.*

### 3. Composite Components
When creating complex UI components (like a Card or a Window), you should override the `add(self, o)` method so that when users do `my_card <= content`, the content goes into the correct inner container, not the root tag.

```python
class Card(Tag.div):
    def init(self, title, **kwargs):
        self["class"] = "card"
        self <= Tag.h2(title)
        self.body = Tag.div(_class="card-body")
        # Use Tag.div.add to bypass the overridden add method during init
        Tag.div.add(self, self.body)

    def add(self, o):
        # Redirect append operations (+-) to the body container
        self.body <= o
```

### 4. State & Reactivity
htag supports both traditional "dirty-marking" and modern reactive `State`.

**Reactive State (Transparent Proxy)**:
- Use `from htag import State`.
- Declare state variables: `self.count = State(0)`.
- Use operators directly: `self.count += 1`, `if self.count > 0: ...` (full support for comparison and math).
- Automatic notification on method calls: `self.items.append("new")`.
- Nested reactivity: `self.data["users"].append(new_user)` works automatically (nested dicts, lists, sets, and tuples are proxied).
- Iterative reactivity: `for item in self.items: item.done = True` works reactively because iteration yields proxies.
- Attribute delegation: `self.user.name = "Bob"` (where `self.user` is a `State(User())`) delegates setting to the underlying object and notifies automatically.
- Type conversions: `int(self.count)`, `bool(self.status)` work transparently.
- Data-driven UIs: `Tag.div(self.count)` or `Tag.div(lambda: f"Count: {self.count}")`.

**Reactive & Boolean Attributes**:
- Attributes support lambdas for dynamic updates: `Tag.div(_class=lambda: "active" if self.is_active else "hidden")`.
- Boolean attributes (e.g., `_disabled`, `_checked`, `_required`) are handled automatically:
    - `True`: Renders the attribute name only (e.g., `disabled`).
    - `False` or `None`: Omits the attribute entirely.

**Rapid Content Updates**:
- Use the `.text` property to quickly replace all text content of a tag: `self.my_label.text = "New Status"`. This completely clears existing children and replaces them with a single string.
**Background Tasks & `update()`**:
- **Automatic Reactivity**: When using `State`, mutations from background tasks (started via `asyncio.create_task`) automatically trigger UI synchronization.
- **Manual Synchronization**: For non-state changes or complex manual updates, every component exposes an `.update()` method (e.g., `self.update()`) which schedules a throttled UI broadcast. 
- **Pattern**: Use `on_mount` to start background tasks and `on_unmount` to cancel them. (This pattern is now robust against page refreshes in `WebApp`).

```python
class App(Tag.App):
    def init(self):
        self.count = State(0)
        Tag.div(self.count)
        
    def on_mount(self):
        async def run():
            while True:
                self.count += 1
                await asyncio.sleep(1)
        self.task = asyncio.create_task(run())

    def on_unmount(self):
        self.task.cancel()
```

**Traditional Reactivity (HTML Attributes & Events)**:
- **HTML Attributes**: 
  - **In Tag Constructors**: Use underscore prefix for keyword arguments: `Tag.div(_class="btn", _id="myid")`. This is only for the constructor.
  - **Direct Management on `self`**: ALWAYS use dictionary syntax. This handles attributes with dashes perfectly and is the modern standard: `self["style"] = "color:red"`, `self["disabled"] = True`, `self["data-test"] = 123`.
  - **Why?**: Assigning to `self.style` (without underscore or brackets) merely sets a private Python attribute that won't be rendered in HTML.
  - Correct: `_class="btn"` (in init), `self["class"] = "btn"`.
  - Incorrect: `class="btn"`, `self._class = "btn"` (deprecated).
- **Events**: Properties set via dictionary keys starting with `on` are mapped to Python callbacks.
  - Example: `self["onclick"] = my_func`

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
htag supports setting custom HTML IDs via `_id="myid"`.
- **Note**: To maintain reactivity with custom IDs, htag automatically injects a `data-htag-id` attribute. The internal communication bridge uses this to ensure partial DOM updates still target the correct element even if the HTML `id` attribute is overridden.

### 5. Forms & Inputs
htag automatically binds input events to Python.
- For text/number inputs, the current value is accessed safely via event handlers: `val = event.value`
- For input elements, the current value is synchronized to the `value` attribute. Access it safely using `self.checkbox["value"]` (or `getattr(self.checkbox, "value", False)` for boolean state).

**Form Submission**:
When using a `Tag.form`, the `submit` event (e.g. `_onsubmit`) receives an `Event` object where `e.value` is a dictionary containing all named form fields (`_name="fieldname"`).
- **Subscript Access**: For convenience, you can access form fields directly on the event object using brackets: `e["fieldname"]` (this is a shortcut for `e.value["fieldname"]`).
- **Standard Pattern**: This aligns with other htag v2 events where the primary data payload is always found in `.value`.

```python
class MySearch(Tag.form):
    def init(self, term=""):
        self <= Tag.input(_name="q", _value=term)
        self <= Tag.input(_type="submit", _value="Search")
        self["onsubmit"] = self.do_search

    @prevent
    def do_search(self, e):
        # e.value is {'q': '...'}
        print(f"Searching for: {e['q']}") 
```

### 6. Resiliency & Fallback
htag implements a robust **3-level transport fallback** mechanism to ensure connectivity in restricted environments:

1.  **Level 1: WebSocket** (Primary): Full bidirectional communication.
2.  **Level 2: SSE (Server-Sent Events)**: Unidirectional push from server; fallback for blocked WebSockets.
3.  **Level 3: Pure HTTP**: Last-resort synchronous POST-based communication.
    - **Buffered Updates**: When no clients are detected, the server buffers UI payloads in a `_fallback_queue`.
    - **Synchronous Response**: The next `/event` POST request retrieves and returns all accumulated updates in a single JSON response.

**Key Robustness Rules**:
- **Global Transport Scope**: For absolute clarity during debugging and to ensure `eval()` calls can always reach them, all transport references should be stored on the global `window` object (e.g., `window.ws`, `window.sse`, `window.use_fallback`).
- **Forceful Termination**: When switching transport modes, previous links must be forcefully "killed" (nullifying references and unhooking listeners) to avoid spectral activity in browser DevTools.
- **Origin Logging**: For debugging, it is a best practice to log the update source: `console.log("htag (WS): updates...", ...)` vs `htag (HTTP): ...`.
- **CSRF & Parano**: All routes are protected by a session-unique CSRF token (`X-HTAG-TOKEN`). `Parano` mode (XOR cipher) provides lightweight obfuscation against MITM proxies.



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
htag includes a built-in visual aid mechanism to help developers track bugs:
- **`Runner(App, debug=True)` (Default)**: During development, ANY error that occurs (a Python exception in a callback, a JavaScript error, or a network disconnection) is visually reported via a Shadow DOM overlay in the screen (displaying js/traceback errors).
- **`Runner(App, debug=False)`**: Use this for production. Tracebacks are logged internally on the server, and only generic "Internal Server Error" messages are shown in the client UI to prevent sensitive data leakage.

### 9. Reactive vs Persistent Trees

When building complex hierarchical structures (like file trees or nested menus), choosing the right rendering strategy is critical for both performance and reliability.

**Dynamic (Lambda-based) Rendering**:
- **Usage**: `Tag.div(lambda: self.render_items(self.data))`
- **Pros**: Very clean, "standard" htag way.
- **Cons**: Every state change triggers a full re-render of the entire branch. In htag, this creates **new Tag objects with new IDs**. If a user clicks an item while another update is happening, the event might be dispatched to an ID that no longer exists in the server-side tree, causing "ghost" clicks or unresponsiveness.

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
            with Tag.div(_class=lambda p=item.path: "" if p in self.expanded else "hidden"):
                if item.children:
                    self.build_tree(item.children) # Recurse
```

### 10. Best Practices for Large Trees

1.  **Stable IDs**: As shown above, prefer persistent tags for elements that handle clicks/inputs.
2.  **CSS Visibility over DOM Removal**: Toggling a `hidden` class is much faster than htag's engine adding/removing elements from the DOM.
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

htag supports "simple events" where the `htag_event` function can be used to pass primitive values (strings, numbers) or custom objects from JavaScript to Python, bypassing the standard DOM Event extraction.

**`onhashchange` support**:
The framework automatically handles the `hashchange` event. When `self["onhashchange"]` is set, the Python callback receives an `event` object with `newURL` and `oldURL` attributes.

```python
class App(Tag.App):
    def init(self):
        self["onhashchange"] = self.on_hash
        
    def on_hash(self, e):
        # e.newURL and e.oldURL are available
        print(f"Navigated to: {e.newURL}")
```

**Custom simple events**:
You can trigger custom events from JavaScript with any data:

```python
# In Python
tag["oncustom"] = lambda e: print(f"Received: {e.value}")

# In JavaScript (via call_js or statics)
htag_event('tag_id', 'custom', 'any string or number')
htag_event('tag_id', 'custom', {any: 'object'})
```

### 13. SPA Router (Hash-Based)

For multi-page behavior in a Single Page Application (SPA), use the built-in `Router`. It maps URL hashes (e.g., `#/users/42`) to component classes and handles synchronization with the browser history.

**Key Features**:
- **Automatic Lifecycle**: `on_mount()` and `on_unmount()` are called automatically when swapping pages.
- **Route Parameters**: Dynamic segments (e.g., `:id`) are injected directly as keyword arguments into the page's `init()`.
- **Programmatic Navigation**: Use `router.navigate("/new-path")` to steer the UI from Python.

```python
from htag import Tag, Router

class HomePage(Tag.div):
    def init(self):
        Tag.h1("Home")
        Tag.a("Go to User 42", _href="#/users/42")

class UserPage(Tag.div):
    def init(self, id: str): # 'id' is extracted from the URL
        self.user_id = id
        Tag.h1(f"User Profile: {id}")
    
    def on_mount(self):
        # Triggered when navigating TO this page
        print(f"Loading user {self.user_id}...")

class App(Tag.App):
    def init(self):
        # 1. Instantiate the Router
        self.router = Router()
        
        # 2. Register routes
        self.router.add_route("/", HomePage)
        self.router.add_route("/users/:id", UserPage)
        
        # 3. Add it to the UI
        self <= self.router
```

**Custom 404**:
Provide a component to handle unmatched routes using `router.set_not_found(My404Component)`. The component will receive the requested path as a `path` keyword argument (if its `init()` accepts it).

### 14. Migrating from htag v1 to v2

If you are migrating legacy htag v1 components, be aware of these core framework changes:

**1. Event Callbacks & Custom Attributes (`e.target`)**:
- *v1*: Callbacks received the triggering object (`def method(self, o):`), and you accessed custom properties directly (`o.info`).
- *v2*: All event callbacks receive a standardized `Event` object (`def method(self, e):`). To access custom attributes passed during component instantiation (like `info=dict(...)`), you MUST use the `target` property: `e.target.info`.
- Form submissions have also been normalized: use `@prevent` on the callback and access form values directly from `e.value` (e.g., `q = e.value["q"]`).

**2. Component Content Replacement (`.clear()`)**:
- *v1*: Often relied on `.set()` or `Content()` wrappers from external component libraries like `htbulma` to replace the inner HTML of a component.
- *v2*: The method to completely replace the contents of any component is natively standard: `.clear(new_child)`. The `.set()` method does not exist on native v2 `Tag` instances.

**3. Move to Composition & Tailwind**:
- Replace heavy Python wrapper components (like `b.VBox`, `b.Progress()`) with native CSS composition (e.g., `Tag.div(_class="flex flex-col")`, `Tag.div(_class="animate-spin")`) leveraging the `.statics` injection of modern CSS frameworks like Tailwind.

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

> **Note**: `styles` is **declarative** (class-level, processed once at init). For **dynamic** styling during interactions, use dictionary syntax or class helpers:
> ```python
> self["style"] = "color: red;"              # inline style
> self.toggle_class("active")              # toggle CSS class
> Tag.div(_class=lambda: "on" if s else "off")  # reactive (init)
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

### Page Title
To set the `<title>` of your application's tab, include a `Tag.title` element in the `statics` list of your main `App` class. htag automatically extracts it to set the initial page title and prevents duplicate title tags in the `<head>`. If omitted, it defaults to the App's class name.

```python
class MyApp(Tag.App):
    statics = [Tag.title("My Awesome App")]
```
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
To prevent constantly closing and re-opening your application window during development, pass `reload=True` to the runner. The master process will watch for changes and restart the child worker server seamlessly.

**Ephemeral Ports (`port=0`)**:
If you run multiple htag apps or tests, you might encounter "Address already in use" errors. Pass `port=0` to the runner to pick an available port automatically. htag will resolve the port and open the browser on the correct URL.
```python
if __name__ == "__main__":
    from htag import ChromeApp
    # Picks a random available port automatically and opens the browser
    ChromeApp(MyApp).run(port=0, reload=True) 
```

## Build standalone executable
When you are in developpment using "uv" (and htag is installed in the venv).
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
