"""
Hash-based SPA Router for htag.

Provides client-side navigation between page components using URL hash fragments.
Each route maps a path pattern (e.g. "/users/:id") to a Tag component class.
Route parameters are injected as keyword arguments into the component's init().

Usage:
    from htag import Tag, Router

    class App(Tag.App):
        def init(self):
            self.router = Router()
            self.router.add_route("/", HomePage)
            self.router.add_route("/users/:id", UserPage)
            self <= self.router
"""
from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any

from .core import GTag, State

logger = logging.getLogger("htag")


@dataclass
class _Route:
    """Internal representation of a registered route."""
    path: str
    component: type[GTag]
    pattern: re.Pattern[str]
    param_names: list[str] = field(default_factory=list)


def _compile_path(path: str) -> tuple[re.Pattern[str], list[str]]:
    """
    Compile a route path pattern into a regex and extract parameter names.

    Examples:
        "/"           → ^/$
        "/users"      → ^/users$
        "/users/:id"  → ^/users/(?P<id>[^/]+)$
    """
    params: list[str] = []
    parts: list[str] = []
    for segment in path.strip("/").split("/"):
        if segment.startswith(":"):
            name = segment[1:]
            params.append(name)
            parts.append(f"(?P<{name}>[^/]+)")
        elif segment:
            parts.append(re.escape(segment))

    if parts:
        pattern = re.compile("^/" + "/".join(parts) + "$")
    else:
        pattern = re.compile("^/$")

    return pattern, params


class Router(GTag):
    """
    Hash-based SPA router component.

    The Router is a Tag.div that listens to hash changes and swaps its content
    to show the component matching the current route. Page components get their
    full lifecycle (on_mount / on_unmount) called automatically.

    Route parameters (e.g. `:id` in `/tasks/:id`) are passed as keyword
    arguments to the page component's init().

    The `path` attribute is a reactive `State("")` holding the current route.
    Use it in lambdas to style active navigation links::

        Tag.a("Home", _href="#/", _class=lambda: "active" if router.path == "/" else "")
    """

    tag: str = "div"

    def init(self, **kwargs: Any) -> None:
        self._routes: list[_Route] = []
        self.path: State = State("")
        self._not_found_component: type[GTag] | None = None

    def add_route(self, path: str, component: type[GTag]) -> None:
        """Register a route mapping a path pattern to a component class."""
        pattern, params = _compile_path(path)
        self._routes.append(_Route(path, component, pattern, params))
        logger.debug("Route registered: %s → %s", path, component.__name__)

    def set_not_found(self, component: type[GTag]) -> None:
        """Set a custom 404 component (optional)."""
        self._not_found_component = component

    def on_mount(self) -> None:
        """Attach to root's hashchange and resolve the initial hash."""
        root = self.root
        if root is not None:
            root["onhashchange"] = self._on_hash_change

        # Wire the event handler for initial route resolution
        # We use a name that htag_event will match
        self["oninit_route"] = self._on_init_route
        
        # Ask the browser for the current hash to resolve the initial route.
        # The JS round-trip is the single source of truth — no server-side
        # fallback to avoid double-rendering when the hash is not "/".
        self.call_js(
            f"setTimeout(() => htag_event('{self.id}', 'init_route', {{hash: window.location.hash}}), 50)"
        )

    def _on_init_route(self, event: Any) -> None:
        """Handle the initial hash value sent from the browser."""
        raw = ""
        if hasattr(event, "hash"):
            raw = event.hash or ""
        elif hasattr(event, "value") and isinstance(event.value, dict):
            raw = event.value.get("hash", "")
        
        logger.debug("Router: received initial hash '%s'", raw)
        path = raw.lstrip("#") or "/"
        if not path.startswith("/"):
            path = "/" + path
        self._navigate_to(path)

    def _on_hash_change(self, event: Any) -> None:
        """Handle browser hashchange events."""
        url: str = getattr(event, "newURL", "") or ""
        logger.debug("Router: hashchange event, newURL='%s'", url)
        if "#" in url:
            path = url.split("#", 1)[1]
        else:
            path = "/"
        if not path.startswith("/"):
            path = "/" + path
        self._navigate_to(path)

    def _navigate_to(self, path: str) -> None:
        """Match a path against registered routes and swap the view."""
        logger.debug("Router: navigating to '%s' (current='%s')", path, self.path)
        if path == self.path and self.path != "":
            return  # Already on this page

        for route in self._routes:
            match = route.pattern.match(path)
            if match:
                params = match.groupdict()
                logger.info("Router match: %s → %s(%s)", path, route.component.__name__, params)
                self._swap(route.component, params)
                self.path.value = path
                return

        # No match → 404
        logger.warning("Router: no route matched for '%s'", path)
        self._swap_not_found(path)
        self.path.value = path

    def _swap(self, component_class: type[GTag], params: dict[str, str]) -> None:
        """Replace the current view with a new component instance."""
        # clear() triggers on_unmount on old content automatically
        self.clear()
        # Instantiate and add — triggers on_mount automatically
        view = component_class(**params)
        self.add(view)

    def _swap_not_found(self, path: str) -> None:
        """Show 404 content."""
        self.clear()
        if self._not_found_component:
            try:
                # Try to pass the path to the custom 404 component
                view = self._not_found_component(path=path)
            except TypeError:
                # Fallback to no-arg instantiation if it fails
                view = self._not_found_component()
            self.add(view)
        else:
            # Default 404 view
            self.add(GTag("div", f"404 — Page not found: {path}"))

    def navigate(self, path: str) -> None:
        """
        Navigate programmatically from Python.

        Changes the browser hash, which triggers onhashchange → _navigate_to.
        This keeps the browser history in sync (Back button works).
        """
        self.call_js(f"window.location.hash='{path}'")
