# SPA Routing

`htag` provides a built-in, lightweight **Hash-Based Router** (`Router`) for building Single Page Applications (SPAs). It allows you to define multiple "pages" as standard components and switch between them seamlessly while maintaining browser history.

## Why Hash-Based?
`htag` uses URL hashes (e.g., `#/about`) for routing. This approach works perfectly with all runners and static file serving without requiring complex server-side redirects (catch-all routes).

## Basic Usage

The `Router` is a component (`Tag.div`) that acts as an "outlet" for your pages.

```python
from htag import Tag, Router, ChromeApp

class HomePage(Tag.div):
    def init(self):
        self <= Tag.h1("Welcome Home")
        self <= Tag.a("Check Page 1", _href="#/page1")

class Page1(Tag.div):
    def init(self):
        self <= Tag.h1("Page 1")
        self <= Tag.a("Back to Home", _href="#/")

class MyApp(Tag.App):
    def init(self):
        # 1. Create a Router
        self.router = Router()

        # 2. Add your routes (Component classes)
        self.router.add_route("/", HomePage)
        self.router.add_route("/page1", Page1)

        # 3. Add the router to the UI
        self <= self.router

if __name__ == "__main__":
    ChromeApp(MyApp).run()
```

## Dynamic Parameters

You can define routes with parameters using the `:name` syntax. These parameters are automatically extracted from the URL and injected into your component's `init()` method as keyword arguments.

```python
class ProfilePage(Tag.div):
    def init(self, user_id: str):
        self.id = user_id
        self <= Tag.h2(f"User Profile: {user_id}")
    
    def on_mount(self):
        print(f"Loading data for user {self.id}...")

# Registering the route
router.add_route("/users/:user_id", ProfilePage)
```

Navigating to `#/users/manatlan` will instantiate `ProfilePage(user_id="manatlan")`.

## Automatic Lifecycle Management

The `Router` handles the full component lifecycle automatically. When you navigate to a new route:
1.  The outgoing component's **`on_unmount()`** is called (if it exists).
2.  The outlet is cleared.
3.  The new component is instantiated.
4.  The new component's **`on_mount()`** is called.

This makes it easy to clean up resources (intervals, watchers) or fetch fresh data on every page change.

## Programmatic Navigation

To navigate from Python without waiting for a user click, use `router.navigate()`:

```python
def on_login_success(self, e):
    self.router.navigate("/dashboard")
```

This method updates the browser hash, ensuring that the **Back/Forward buttons** continue to work as expected.

## Active Route Styling (`router.path`)

The `router.path` attribute is a reactive `State("")` that always reflects the current route. Use it in lambda attributes to **automatically highlight active navigation links** or tabs:

```python
class MyApp(Tag.App):
    def init(self):
        self.router = Router()
        self.router.add_route("/", HomePage)
        self.router.add_route("/settings", SettingsPage)

        # Navigation links with automatic "active" class
        with Tag.nav():
            Tag.a("Home",     _href="#/",         _class=lambda: "active" if self.router.path == "/" else "")
            Tag.a("Settings", _href="#/settings",  _class=lambda: "active" if self.router.path == "/settings" else "")

        self <= self.router
```

Since `path` is a standard htag `State`, it integrates with the full reactivity system — any component observing it will re-render automatically when the route changes.

## Custom 404 Pages

If no route matches the current path, a default "404 Not Found" message is displayed. You can customize this by providing your own component:

```python
class MyNotFound(Tag.div):
    def init(self, path=None):
        self <= Tag.h1("Ouch! Where are we?")
        self <= Tag.p(f"I couldn't find path: {path}")

router.set_not_found(MyNotFound)
```

---

[← Advanced](advanced.md) | [Back to Home](../README.md)
