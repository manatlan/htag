class HtagError(Exception):
    """Base class for all htag exceptions."""
    pass


class HtagRenderError(HtagError):
    """Raised when there is an error rendering a component."""
    pass


class HtagEventError(HtagError):
    """Raised when an error occurs during an event callback execution."""
    pass
