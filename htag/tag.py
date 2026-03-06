from __future__ import annotations

from .core import GTag, App


class TagCreator:
    def __init__(self) -> None:
        self._registry: dict[str, type[GTag]] = {}

    def __getattr__(self, name: str) -> type[GTag]:
        """
        Dynamically creates GTag subclasses on the fly.
        Allows using 'Tag.Div(...)', 'Tag.Button(...)', etc.
        """
        if name in self._registry:
            return self._registry[name]

        if name == "App":
            return App

        # Create a dynamic subclass of GTag
        tag_name = name.lower().replace("_", "-")
        # We cache it in registry for performance and consistency
        new_class = type(name, (GTag,), {"tag": tag_name})
        self._registry[name] = new_class
        return new_class


Tag = TagCreator()  # Singleton instance
