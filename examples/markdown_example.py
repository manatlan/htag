import htag
from htag import Tag, App, HTML
import mistune

class MarkdownViewer(Tag.div):
    """
    A simple component that renders Markdown text to raw HTML.
    It uses the `HTML` string wrapper to prevent `htag` from escaping the rendered HTML.
    """
    def __init__(self, markdown_text: str, **kwargs):
        super().__init__(**kwargs)

        # We process the markdown into an HTML string
        rendered_html_string = mistune.html(markdown_text)

        # We wrap the result in htag.HTML to mark it as safe, avoiding XSS escapes
        # and we append it as a child to our component.
        self += HTML(rendered_html_string)

class MarkdownExample(App):
    """ Main Application demonstrating the markdown bypass. """
    def init(self):
        self += Tag.h1("Markdown Render Example")
        self += Tag.p("The following block is rendered from markdown:")

        # An example of markdown content
        md_content = '''
## Hello Markdown!

This is a **bold** statement and this is *italic*.

- Item 1
- Item 2
- Item 3

You can even add code blocks:
```python
print("Hello World")
```
        '''

        # Apply the markdown viewer component with some CSS styles
        self += MarkdownViewer(
            markdown_text=md_content,
            style="border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9;"
        )

if __name__ == "__main__":
    import uvicorn
    from htag import WebApp

    app = WebApp(MarkdownExample)
    uvicorn.run(app, host="127.0.0.1", port=8000)
