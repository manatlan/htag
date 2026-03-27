# 🛠️ Htag v2 Core Improvements (Technical "To Fix")

This document outlines technical friction points encountered while developing the `htag.ui` library and proposes architectural improvements for the `htag` v2 core.

---

## 1. GTag Reactivity for Shadow Tags (`<style>`, `<script>`)

### 🚩 Problem
In `htag/core.py`, the `GTag.__init__` method contains a hardcoded rule that strips IDs from `style` and `script` tags:
```python
if getattr(self, "tag", None) in ("style", "script"):
    self.id = ""
```
**Consequence:** Any `GTag` using these tags is "invisible" to the server-side update mechanism. Even if a child lambda changes its output, the server cannot send a partial DOM update because there is no ID to target in the browser.

### ✅ Proposed Fix
Allow these tags to have a unique ID if they are dynamic.
*   **Logic:** If the tag is a `style` or `script` AND it has callable children OR is marked as dynamic, keep/assign a stable `id`.

---

## 2. Automatic State De-referencing in `_eval_child` ✅ FIXED

### ✅ Fix
Update `_eval_child` to automatically return `child.value` if `child` is a `State` instance.
*   **Logic:** Add an `isinstance(child, State)` check in `_eval_child` to return the underlying value.
*   **Bonus:** This also removes the need for `State.__call__`.

---

## 3. Reactive Attributes (Auto-Observation) ✅ FIXED

### ✅ Fix
Make the `_render_attrs` method register the `GTag` as an observer of any `State` object encountered in its attribute dictionary.
*   **Logic:** In `_eval_child` (called by `_render_attrs`), set `_ctx.current_eval = self` when de-referencing a `State` object to ensure the tag observes it.

---

## 4. Component Scoping vs. Dynamic Classes

### 🚩 Problem
When a component class defines `styles = "..."`, `GTag` automatically adds a scoped class (e.g., `.htag-Button`) to the tag in `__init__`. 
If a developer also defines `self["class"] = lambda: ...` in `init()`, subsequent calls to `add_class()` (triggered by the core) will crash because they try to call `.split()` on the lambda function instead of a string.

### ✅ Proposed Fix
Improve `_update_classes` to handle cases where `self.__attrs["class"]` is a callable.
*   **Logic:** If `class` is a callable, either wrap it or ensure scoping is appended to the lambda result.

---

## 5. GTag Convenience Properties (Attribute Proxies)

### 🚩 Problem
In event handlers, `e.target` is a `GTag` object. Accessing common HTML attributes requires `e.target["value"]`, which is inconsistent with browser JS (`e.target.value`).
```python
# This fails in htag v2
onchange = lambda e: print(e.target.value) 
```

### ✅ Proposed Fix
Add common property proxies to the `GTag` base class (or via `TagCreator`).
*   **Logic:** Implement `@property def value(self): return self["value"]` and similar for `checked`, `id`, `name`, `src`, `href`.

---

## 6. Event Payload Extraction (Checkboxes)

### 🚩 Problem
The current `client_js.py` extracts `target.checked` for checkboxes and puts it in `data.value`.
```javascript
else if (target.type === 'checkbox') {
    data.value = target.checked;
}
```
**Consequence:** On the Python side, `e.value` is the boolean, but `e.checked` or `e.target.checked` (expected by some developers) is `None`.

### ✅ Proposed Fix
Consistency in the `Event` object: if the payload has a single value, ensure it is accessible via multiple expected names or via a unified `target` state.

---

## 7. Native Lifecycle Events (`onremove`)

### 🚩 Problem
There is no built-in way for the browser to notify the Python server that a tag has been removed from the DOM (e.g. by a third-party JS library or internal logic). Current components use `setTimeout` + custom event hacks.
```python
# The current "hack"
self.call_js(f"setTimeout(() => htag_event('{self.id}', 'remove', null), 3000)")
self["onremove"] = lambda e: self.remove()
```

### ✅ Proposed Fix
Standardize a `remove` event that `GTag` understands natively, and hook it up to the browser-side deletion logic (potentially using the `onunmount` lifecycle hook already in Python).

---

## 8. Fragment Reactivity (`Tag(None)`)

### 🚩 Problem
Fragments (`GTag(None, ...)`) don't have a representation in the DOM, so they don't have an ID. If a fragment contains a reactive lambda, and that lambda's state changes, the partial update fails because there is no target element.

```python
# Example of the "Fragment Trap"
with Tag.div():
    with Tag(None) as fragment:
        # If self.state changes, this SHOULD update.
        # But fragment has no ID, so updates[fragment.id] -> updates[""]
        # The browser never receives the update.
        fragment += lambda: f"State is: {self.state}"
```

### ✅ Proposed Fix
If a component that needs updating is a fragment, the framework should intelligently "climb up" the parent tree until it finds a physical tag (with an ID) and trigger an update on that parent instead.

---

## 9. IDE DX (Type Stubs for Dynamic Tags)

### 🚩 Problem
`Tag.Div`, `Tag.Button` have no type information. IDEs see them as `Any`.

### ✅ Proposed Fix
Provide a `.pyi` stub file that defines common HTML tags as `GTag` subclasses to enable autocompletion for attributes like `_class`, `_style`, `_onclick`, etc.
