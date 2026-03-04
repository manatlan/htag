import os
import json
from htag import Tag, ChromeApp, State

class AceEditor(Tag.div):
    """A GTag component wrapping the Ace Editor."""
    statics = [
        Tag.script(_src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/ace.js"),
    ]

    styles = """
        .editor-container {
            width: 100%;
            height: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    """

    def init(self, value: str = "", language: str = "python", **kwargs):
        self.add_class("editor-container")
        self._value = value
        self._language = language

    def on_mount(self):
        # Initialize Ace Editor on the client side, waiting for the library AND the DOM element
        val = json.dumps(self._value)
        script = f"""
            (function initAce() {{
                var el = document.getElementById("{self.id}");
                if (typeof ace !== 'undefined' && el) {{
                    ace.config.set('basePath', 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/');
                    var editor = ace.edit(el);
                    editor.setTheme("ace/theme/monokai");
                    editor.session.setMode("ace/mode/{self._language}");
                    editor.setValue({val}, -1);
                    
                    // Sync content back to Python on change (debounced)
                    editor.session.on('change', function() {{
                        var content = editor.getValue();
                        el._ace_content = content;
                    }});
                    console.log("Ace Editor initialized for {self.id}");
                }} else {{
                    console.log("Waiting for Ace or DOM element {self.id}...");
                    setTimeout(initAce, 100);
                }}
            }})();
        """
        self.call_js(script)

    def set_value(self, value: str):
        print(f"AceEditor.set_value called with {len(value)} chars")
        self._value = value
        val = json.dumps(value)
        # We re-set the mode every time to ensure highlighting is applied to new content
        self.call_js(f"""
            (function setVal() {{
                var el = document.getElementById("{self.id}");
                if (typeof ace !== 'undefined' && el) {{
                    var ed = ace.edit(el);
                    ed.setValue({val}, -1);
                    ed.session.setMode("ace/mode/{self._language}");
                    console.log("Value & Mode set in editor {self.id}");
                }} else {{
                    console.log("set_value: Waiting for Ace or DOM element...");
                    setTimeout(setVal, 100);
                }}
            }})();
        """)

    def get_value(self, event):
        # This is a helper to extract the value from the client-side property
        # when an event is triggered from this component
        return getattr(event, "value", "")

class App(Tag.App):
    statics = [
        Tag.script(_src="https://cdn.tailwindcss.com"),
        Tag.style("""
            body { background: #f3f4f6; font-family: 'Inter', sans-serif; }
            .sidebar { width: 250px; background: white; border-right: 1px solid #e5e7eb; overflow-y: auto; }
            .main { flex: 1; display: flex; flex-direction: column; height: 100vh; }
            .editor-wrapper { flex: 1; padding: 20px; position: relative; }
            .file-item { padding: 10px 20px; cursor: pointer; border-bottom: 1px solid #f3f4f6; transition: background 0.2s; }
            .file-item:hover { background: #f9fafb; }
            .file-item.active { background: #eff6ff; border-left: 4px solid #3b82f6; color: #1e40af; font-weight: 500; }
        """)
    ]

    def init(self):
        self.current_file = State(None)
        self.files = [f for f in os.listdir(".") if f.endswith(".py")]
        self.files.sort()
        print(f"App init: found {len(self.files)} files")

        with Tag.div(_class="flex h-screen"):
            # Sidebar
            with Tag.div(_class="sidebar"):
                Tag.div("Python Files", _class="p-5 font-bold text-gray-700 bg-gray-50 border-bottom")
                with Tag.div():
                    for f in self.files:
                        # Use fine-grained reactivity for classes
                        item = Tag.div(f, _onclick=lambda e, f=f: self.load_file(f))
                        item._class = lambda f=f, item=item: f"file-item {'active' if self.current_file.value == f else ''}"

            # Main Area
            with Tag.div(_class="main"):
                # Header
                with Tag.div(_class="p-4 bg-white border-b flex justify-between items-center"):
                    Tag.div(lambda: self.current_file.value or "Select a file", _class="font-mono text-sm text-gray-600")
                    with Tag.div():
                        Tag.button("Save", _class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm", 
                                   _onclick=self.save_file, _disabled=lambda: self.current_file.value is None)

                # Editor
                with Tag.div(_class="editor-wrapper"):
                    self.editor = AceEditor("")

    def load_file(self, filename):
        print(f"Loading file: {filename}")
        self.current_file.value = filename
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Read {len(content)} chars from {filename}")
            self.editor.set_value(content)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            self.editor.set_value(f"# Error loading file: {e}")

    def save_file(self, event):
        if self.current_file.value:
            # We need to get the value from the JS side.
            self.call_js(f"""
                (function save() {{
                    var el = document.getElementById('{self.editor.id}');
                    if (typeof ace !== 'undefined' && el) {{
                        var content = ace.edit(el).getValue();
                        htag_event('{self.editor.id}', 'save', {{target: {{value: content}}}});
                    }} else {{
                        console.error("Cannot save: Ace or element not ready");
                    }}
                }})();
            """)

    def _on_editor_save(self, event):
        # This is a custom event handler triggered by the JS above
        content = event.value
        filename = self.current_file.value
        print(f"Saving {filename} ({len(content) if content is not None else 'None'} bytes)")
        if filename and content is not None:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Saved {filename}")
            except Exception as e:
                print(f"Error saving {filename}: {e}")
        else:
            print(f"Save aborted: content is None or no filename")

    def on_mount(self):
        # Register the custom event handler on the editor component
        # htag2 allows dynamic event binding
        self.editor._onsave = self._on_editor_save

if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(App).run(reload=False)
