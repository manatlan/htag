# htag2

<p align="center">
  <img src="https://manatlan.github.io/htag2/assets/logo.png" width="300" alt="htag2 logo">
</p>

<p align="center">
  <a href="https://pypi.org/project/htag2/">
    <img src="https://img.shields.io/pypi/v/htag2?style=for-the-badge&logo=pypi&color=blue" alt="PyPI">
  </a>
  <a href="https://github.com/manatlan/htag2/actions/workflows/tests.yml">
    <img src="https://img.shields.io/github/actions/workflow/status/manatlan/htag2/tests.yml?branch=main&style=for-the-badge&logo=github&label=Tests" alt="Test Status">
  </a>
  <a href="https://github.com/manatlan/htag2/releases/tag/latest">
    <img src="https://img.shields.io/badge/Download-Latest_Build-blue?style=for-the-badge&logo=github" alt="Download Latest Build">
  </a>
</p>

Here is a full rewrite of [htag](https://github.com/manatlan/htag), using only antigravity and prompts/intentions.

It feels very good. Currently, it's not a replacement, it's just a POC.

It's completely crazy, but it works :

- For building desktop apps (ChromeApp on linux/windows)
- For building web apps (WebApp as an asgi app (for starlette/fastapi/...))
- For building SPA HTML Page (with the PyScript runner)
- For building android apps ([it works](examples/app_android/README.md), **but need to improve**)


## Get Started

Check the [Official Documentation](https://manatlan.github.io/htag2/) for more information.

## Install

```bash
uv add htag2
```

Or using pip:
```bash
pip install htag2
```

Alternatively, you can run from source:
```bash
git clone https://github.com/manatlan/htag2.git
cd htag2
uv run examples/main3.py
```

### Skill

With gemini-cli, claude-code, mistral-vibe (or others), you can use this [SKILL.md](.agent/skills/htag2-development/SKILL.md) to create a htag2 application.


## Antigravity resumes :

htag2 is a Python library for building web applications using HTML, CSS, and JavaScript.

### Key Resiliency Features Added
*   **Zero-Config Hot-Reload**: Passing `reload=True` to any runner (e.g. `ChromeApp(App).run(reload=True)`) automatically watches for Python file changes, seamlessly restarts the backend, and gracefully refreshes the frontend without losing your browser window session.
*   **F5/Reload Robustness**: Refreshing the browser no longer kills the Python backend; the session reconstructs cleanly.
*   **HTTP Fallback (SSE + POST)**: If WebSockets are blocked (e.g. strict proxies) or fail to connect, the client seamlessly falls back to HTTP POST for events and Server-Sent Events (SSE) for receiving UI updates.
*   **Production Debug Mode**: Easily disable error reporting in the client by setting `debug=False` on the runner (e.g. `WebApp(App, debug=False).app`), preventing internal stacktraces from leaking to users.
*   **Parano Mode (Payload Obfuscation)**: By initializing `WebApp(App, parano=True)`, all data exchanged between the frontend and backend is automatically obfuscated using a dynamic XOR cipher and Base64 wrapping, making network traffic unreadable to MITM proxies.

### New API Features
*   **`.root`, `.parent`, and `.childs` properties**: Every `GTag` exposes its position in the component tree. `.root` references the main `Tag` instance, `.parent` references the direct parent component, and `.childs` is a list of its children. This allows components to easily navigate the DOM tree and trigger app-level actions.
*   **Declarative UI with Context Managers (`with`)**: You can now build component trees visually using `with` blocks (e.g., `with Tag.div(): Tag.h1("Hello")`), removing the need for `self <= ...` boilerplate.
*   **Dual Attribute Access (Dictionary Style)**: In addition to `self._class = "foo"`, you can now use `self["class"] = "foo"`. This is the preferred way to handle attributes with dashes (e.g., `self["data-id"] = 123`).
*   **Automatic Attribute Normalization**: HTML attributes are normalized to use dashes internally. Setting `self._data_id = "123"` is strictly equivalent to setting `self["data-id"] = "123"`.
*   **Reactive State Management (`State`)**: Introducing `State(value)` for automatic UI reactivity. Simply assign a `State` to a component directly (e.g. `Tag.div(state)`) or using a lambda (e.g. `Tag.div(lambda: state.value)`), and the UI will auto-update whenever the state changes. Use `state.set(new_value)` for functional updates inside callbacks.
*   **Reactive & Boolean Attributes**: Attributes like `_class`, `_style`, or `_disabled` now support lambdas for dynamic updates. Boolean attributes (e.g. `_disabled=True`) are correctly rendered as key-only or omitted.
*   **Simplified Removal (`.remove()`)**: To remove a component from its parent, simply call `self.remove()` without arguments.
*   **Rapid Content Replacement (`.text`)**: Use the `.text` property on any tag to quickly replace its inner text content without needing to manually clear its children first.
*   **Recursive Statics & JS**: Components created dynamically (via lambdas) now have their `statics` (CSS) and `call_js` commands correctly collected and sent to the client.
*   **Scoped Styles (`styles`)**: Define a `styles` class attribute on any component to get automatically scoped CSS. The framework prefixes every rule with `.htag-ClassName`, handles `@media`, `@keyframes`, pseudo-selectors, and multi-selectors.
*   **CSS Class Helpers**: `add_class()`, `remove_class()`, `toggle_class()`, and `has_class()` for convenient class manipulation without manual string handling.
*   **`State.notify()`**: Manually trigger reactive updates after in-place mutations of mutable values (lists, dicts).
*   **Simple Events & HashChange**: Support for passing primitive values or custom objects from JS (via `tag["onclick"] = func` or `tag._onclick = func`). Includes built-in support for `_onhashchange`.
*   **Fragments (`Tag()`)**: Create virtual components that group children without adding a wrapper tag to the DOM.
*   **Advanced Tag Search (`.find_tag()`)**: Effortlessly locate any component in the tree by its internal htag ID or its manually assigned HTML `id`.
*   **Custom ID Resilience**: Manual HTML `id` attributes are now supported without breaking htag2's reactive partial updates, thanks to an automatic `data-htag-id` fallback mechanism.
*   **Automatic Attribute Assignment**: Non-prefixed keyword arguments passed during component instantiation are automatically assigned as instance attributes, simplifying data passing to custom components.
