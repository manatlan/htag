# htag 2

<p align="center">
  <img src="https://manatlan.github.io/htag/assets/logo.png" width="300" alt="htag logo">
</p>

<p align="center">
  <a href="https://pypi.org/project/htag/">
    <img src="https://img.shields.io/pypi/v/htag?style=for-the-badge&logo=pypi&color=blue" alt="PyPI">
  </a>
  <a href="https://github.com/manatlan/htag/actions/workflows/tests.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/manatlan/htag/tests.yml?branch=main&style=for-the-badge&logo=github&label=Tests" alt="Test Status">
  </a>
  <a href="https://github.com/manatlan/htag/releases/tag/latest">
    <img src="https://img.shields.io/badge/Download-Latest_Build-blue?style=for-the-badge&logo=github" alt="Download Latest Build">
  </a>
</p>

**htag** is a Python3 GUI toolkit for building "beautiful" applications for mobile, web, and desktop from a single codebase

Here is a full rewrite of **htag 1.0.0**, using only antigravity and prompts/intentions. It's the future of **htag**.

Currently, it works ...

- For building desktop apps (ChromeApp on linux/windows/mac, or simple WebApp)
- For building web apps (WebApp as an asgi app (for starlette/fastapi/...))
- For building SPA HTML Page (with the PyScript runner)
- For building android apps ([it works](examples/app_android/README.md), **but need to improve**)

## Major differences between v1 and v2

- A lot simpler & more reactive
- `Tag.App` is the main app component
- Full starlette compliant from the ground
- Websocket communication, if fails : fallback to HTTP SSE
- No more generic Runner
- State object for reactivity
- DX: errors are a lot better handled/viewable, hot-reload available
- Better events
- less boilerplate (kiss minded)
- Styles can be scoped by component
- ...


## Get Started

Check the [Official V2 Documentation](https://manatlan.github.io/htag/) for more information. [old v1 docs](https://manatlan.github.io/htag/v1/)


## Install

```bash
uv add htag -U
```

Or using pip:
```bash
pip install -U htag
```

Alternatively, you can run from source:
```bash
git clone https://github.com/manatlan/htag.git
cd htag
uv run examples/main3.py
```

### Skill

With agentic llm, you can use this [SKILL.md](.agent/skills/htag-development/SKILL.md) to create an htag application.


## Antigravity resumes :

htag is a Python library for building web applications using HTML, CSS, and JavaScript.

### New Features
*   **Zero-Config Hot-Reload**: Passing `reload=True` to any runner (e.g. `ChromeApp(App).run(reload=True)`) automatically watches for Python file changes, seamlessly restarts the backend, and gracefully refreshes the frontend without losing your browser window session.
*   **F5/Reload Robustness**: Refreshing the browser no longer kills the Python backend; the session reconstructs cleanly.
*   **HTTP Fallback (SSE + POST)**: If WebSockets are blocked (e.g. strict proxies) or fail to connect, the client seamlessly falls back to HTTP POST for events and Server-Sent Events (SSE) for receiving UI updates.
*   **Production Debug Mode**: Easily disable error reporting in the client by setting `debug=False` on the runner (e.g. `WebApp(App, debug=False).app`), preventing internal stacktraces from leaking to users.
*   **Parano Mode (Payload Obfuscation)**: By initializing `WebApp(App, parano=True)`, all data exchanged between the frontend and backend is automatically obfuscated using a dynamic XOR cipher and Base64 wrapping, making network traffic unreadable to MITM proxies.
*   **Progressive UI in Lifecycle Hooks**: Both `on_mount()` and `on_unmount()` fully support yielding intermediate UI states natively. `htag` intelligently queues `on_mount` generators until the client establishes a connection, and gracefully processes `on_unmount` broadcasts.
*   **`.root`, `.parent`, and `.childs` properties**: Every `GTag` exposes its position in the component tree. `.root` references the main `Tag` instance, `.parent` references the direct parent component, and `.childs` is a list of its children. This allows components to easily navigate the DOM tree and trigger app-level actions.
*   **Declarative UI with Context Managers (`with`)**: You can now build component trees visually using `with` blocks (e.g., `with Tag.div(): Tag.h1("Hello")`), removing the need for `self <= ...` boilerplate.
*   **Modern Attribute Access (Dictionary Style)**: In addition to `Tag.div(_class="foo")` in constructors, you must now use `self["class"] = "foo"` for dynamic property management after instantiation. This is the only way to handle all attributes, including those with dashes (e.g., `self["data-id"] = 123`).
*   **Reactive State Management (`State`)**: Introducing `State(value)` for automatic UI reactivity. `State` acts as a transparent **Proxy**: you can use comparison/arithmetic operators directly (`if self.count > 0: ...`), mutate nested structures (including `lists`, `dicts`, `sets`, and `tuples`), and delegate attribute assignments seamlessly.
*   **Iterative & Attribute Reactivity**: Iterating over a `State` now yields proxies, meaning mutations like `for item in self.list: item.active = True` trigger re-renders. Attribute assignments (e.g. `self.user.name = "Bob"`) are automatically delegated to the underlying object and notified.
*   **Reactive & Boolean Attributes**: Attributes like `_class`, `_style`, or `_disabled` in constructors now support lambdas for dynamic updates. Boolean attributes (e.g. `_disabled=True`) are correctly rendered as key-only or omitted.
*   **Simplified Removal (`.remove()`)**: To remove a component from its parent, simply call `self.remove()` without arguments.
*   **Rapid Content Replacement (`.text`)**: Use the `.text` property on any tag to quickly replace its inner text content without needing to manually clear its children first.
*   **Recursive Statics & JS**: Components created dynamically (via lambdas) now have their `statics` (CSS) and `call_js` commands correctly collected and sent to the client.
*   **Scoped Styles (`styles`)**: Define a `styles` class attribute on any component to get automatically scoped CSS. The framework prefixes every rule with `.htag-ClassName`, handles `@media`, `@keyframes`, pseudo-selectors, and multi-selectors.
*   **CSS Class Helpers**: `add_class()`, `remove_class()`, `toggle_class()`, and `has_class()` for convenient class manipulation without manual string handling.
*   **Simple Events & HashChange**: Support for passing primitive values or custom objects from JS (via `tag["onclick"] = func`). Includes built-in support for `onhashchange`.
*   **Fragments (`Tag()`)**: Create virtual components that group children without adding a wrapper tag to the DOM.
*   **Advanced Tag Search (`.find_tag()`)**: Effortlessly locate any component in the tree by its internal htag ID or its manually assigned HTML `id`.
*   **Custom ID Resilience**: Manual HTML `id` attributes are now supported without breaking htag's reactive partial updates, thanks to an automatic `data-htag-id` fallback mechanism.
*   **Automatic Attribute Assignment**: Non-prefixed keyword arguments passed during component instantiation are automatically assigned as instance attributes, simplifying data passing to custom components.
*   **Unified Form Handling**: When a `Tag.form` is submitted, all input fields are automatically collected into a dictionary and passed as `event.value`. You can conveniently access fields using square brackets on the event object (e.g., `e["fieldname"]`).


## History

At the beginning, there was [guy](https://github.com/manatlan/guy), which was/is the same concept as [python-eel](https://github.com/ChrisKnott/Eel), but more advanced.
One day, I've discovered [remi](https://github.com/rawpython/remi), and asked my self, if it could be done in a *guy way*. The POC was very good, so I released
a version of it, named [gtag](https://github.com/manatlan/gtag). It worked well despite some drawbacks, but was too difficult to maintain. So I decided to rewrite all
from scratch, while staying away from *guy* (to separate, *rendering* and *runners*)... and [htag](https://github.com/manatlan/htag/tree/v1-legacy) was born. The codebase is very short, concepts are better implemented, and it's very easy to maintain. And now (2026) [htag v2](https://github.com/manatlan/htag) is here (a full rewrite of v1 with antigravity) !

