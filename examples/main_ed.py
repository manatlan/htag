import os
import asyncio
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
            border: none;
            border-radius: 0;
        }
    """

    def init(self, value: str = "", language: str = "python", **kwargs):
        self.add_class("editor-container")
        self._ace_value = value
        self._ace_language = language

    def on_mount(self):
        # Initialize Ace Editor on the client side, waiting for the library AND the DOM element
        val = json.dumps(self._ace_value)
        script = f"""
            (function initAce() {{
                var el = document.getElementById("{self.id}");
                if (typeof ace !== 'undefined' && el) {{
                    ace.config.set('basePath', 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.32.7/');
                    var editor = ace.edit(el);
                    editor.setTheme("ace/theme/cobalt");
                    editor.session.setMode("ace/mode/{self._ace_language}");
                    editor.setFontSize(15);
                    el._ace_loading = true;
                    editor.setValue({val}, -1);
                    setTimeout(function() {{ el._ace_loading = false; }}, 100);
                    
                    // Sync content back to Python on change (manual save only)
                    editor.session.on('change', function(e) {{
                        el._ace_content = editor.getValue();
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
        self._ace_value = value
        val = json.dumps(value)
        # We re-set the mode every time to ensure highlighting is applied to new content
        self.call_js(f"""
            (function setVal() {{
                var el = document.getElementById("{self.id}");
                if (typeof ace !== 'undefined' && el) {{
                    var ed = ace.edit(el);
                    el._ace_loading = true;
                    ed.setValue({val}, -1);
                    setTimeout(function() {{ el._ace_loading = false; }}, 100);
                    ed.setTheme("ace/theme/cobalt");
                    ed.session.setMode("ace/mode/{self._ace_language}");
                    ed.setFontSize(15);
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
            body { background: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; }
            .sidebar { width: 250px; background: #1e293b; border-right: 1px solid #334155; overflow-y: auto; }
            .main { flex: 1; display: flex; flex-direction: column; height: 100vh; }
            .editor-wrapper { flex: 1; padding: 0; position: relative; background: #0f172a; }
            .file-item { padding: 10px 20px; cursor: pointer; border-bottom: 1px solid #334155; transition: background 0.2s; color: #cbd5e1; }
            .file-item:hover { background: #334155; }
            .file-item.active { background: #1e3a8a; border-left: 4px solid #3b82f6; color: #f8fafc; font-weight: 500; }
            
            /* Custom Scrollbars */
            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-track { background: #0f172a; }
            ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; border: 1px solid #1e293b; }
            ::-webkit-scrollbar-thumb:hover { background: #475569; }
            * { scrollbar-width: thin; scrollbar-color: #334155 #0f172a; }

            /* Notifications */
            .toast-container { position: fixed; bottom: 20px; right: 20px; z-index: 1000; display: flex; flex-direction: column; gap: 10px; }
            .toast { 
                padding: 12px 20px; border-radius: 8px; font-size: 14px; min-width: 250px; 
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4); border: 1px solid rgba(255,255,255,0.1);
                animation: toast-in 0.3s ease-out forwards;
            }
            @keyframes toast-in { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            .toast-success { background: #15803d; color: white; border-color: #16a34a; }
            .toast-error { background: #b91c1c; color: white; border-color: #dc2626; }
            .toast-info { background: #1e40af; color: white; border-color: #2563eb; }
        """)
    ]

    def init(self):
        self.current_file = State(None)
        self.expanded_dirs = State(set())
        self.files_tree = self.scan_directory(".")
        
        # Flattened list for auto-load first file logic
        self.all_py_files = []
        def flatten(items):
            for i in items:
                if i["type"] == "file": self.all_py_files.append(i["path"])
                else: flatten(i["children"])
        flatten(self.files_tree)

        with Tag.div(_class="flex h-screen"):
            # Sidebar
            with Tag.div(_class="sidebar"):
                Tag.div("Project Files", _class="p-5 font-bold text-gray-300 bg-slate-800 border-b border-slate-700")
                with Tag.div(_class="py-2"):
                    self.build_tree(self.files_tree)

            # Main Area
            with Tag.div(_class="main"):
                # Header
                with Tag.div(_class="p-4 bg-slate-800 border-b border-slate-700 flex justify-between items-center"):
                    Tag.div(lambda: self.current_file.value or "Select a file", _class="font-mono text-sm text-gray-400")
                    Tag.button("Save", 
                               _class=lambda: f"bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm {'hidden' if self.current_file.value is None else ''}", 
                               _onclick=self.save_file)

                # Content Area (Editor + Placeholder)
                with Tag.div(_class="editor-wrapper"):
                    # Welcome Placeholder
                    with Tag.div(_class=lambda: f"h-full flex flex-col items-center justify-center text-gray-500 {'hidden' if self.current_file.value else ''}"):
                        Tag.span("🐍", style="font-size: 64px; opacity: 0.2;")
                        Tag.p("Select a Python file to start editing", _class="mt-4 text-center")
                    
                    # The Editor
                    self.editor_wrapper = Tag.div(_class=lambda: f"h-full {'hidden' if self.current_file.value is None else ''}")
                    self.ace_editor = AceEditor("", _onsave=self._on_editor_save)
                    Tag.div.add(self.editor_wrapper, self.ace_editor)
                
                # Notifications Container
                self.toast_container = Tag.div(_class="toast-container")

    def scan_directory(self, path):
        items = []
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for entry in entries:
                if entry.name.startswith((".", "__")) or entry.name in ("venv", ".venv", "node_modules", ".git", "__pycache__"):
                    continue
                if entry.is_dir():
                    sub_items = self.scan_directory(entry.path)
                    if sub_items:
                        items.append({"name": entry.name, "type": "dir", "path": entry.path, "children": sub_items})
                elif entry.name.endswith(".py"):
                    items.append({"name": entry.name, "type": "file", "path": entry.path})
        except PermissionError:
            pass
        return items

    def build_tree(self, items, level=0):
        for item in items:
            path = os.path.normpath(item["path"])
            
            if item["type"] == "dir":
                # Folder Row
                with Tag.div(_class="file-item flex items-center", 
                           _onclick=lambda e, p=path: self.toggle_dir(p),
                           style="padding-left: 8px"):
                    Tag.span(lambda p=path: "▼" if p in self.expanded_dirs.value else "▶", 
                             _class="mr-1 text-[10px] text-gray-500 w-3 inline-block")
                    Tag.span("📁", _class="mr-2 opacity-70")
                    Tag.span(item["name"], _class="truncate")
                
                # Children Container (Nested with margin and border)
                with Tag.div(_class=lambda p=path: "ml-4 border-l border-slate-700/50" if p in self.expanded_dirs.value else "hidden"):
                    self.build_tree(item["children"], level + 1)
            else:
                # File Row
                with Tag.div(_class=lambda p=path: f"file-item flex items-center {'active' if self.current_file.value == p else ''}", 
                           _onclick=lambda e, p=path: self.load_file(p),
                           style="padding-left: 24px"):
                    Tag.span("📄", _class="mr-2 opacity-70")
                    Tag.span(item["name"], _class="truncate")

    def toggle_dir(self, path):
        path = os.path.normpath(path)
        current = set(self.expanded_dirs.value)
        if path in current:
            current.remove(path)
        else:
            current.add(path)
        self.expanded_dirs.set(current)

    def load_file(self, filename):
        self.current_file.value = filename
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Read {len(content)} chars from {filename}")
            self.ace_editor.set_value(content)
        except Exception as e:
            msg = f"Error loading {filename}: {e}"
            print(msg)
            self.notify(msg, "error")
            self.ace_editor.set_value(f"# Error loading file: {e}")

    def notify(self, message, type="info"):
        """Show a toast notification."""
        t_class = f"toast toast-{type}"
        # Create toast with an 'expire' event that removes itself
        t = Tag.div(message, _class=t_class, _onexpire=lambda e: t.remove())
        # The above used _onexpire in instantiation (STILL VALID)
        # But if we were to set it later:
        # t["onexpire"] = lambda e: t.remove()
        self.toast_container.add(t)
        
        # Trigger the 'expire' event from client-side after 5 seconds
        t.call_js(f"setTimeout(() => htag_event('{t.id}', 'expire', {{}}), 5000)")

    def save_file(self, event):
        if self.current_file.value:
            # We need to get the value from the JS side.
            self.call_js(f"""
                (function save() {{
                    var el = document.getElementById('{self.ace_editor.id}');
                    if (typeof ace !== 'undefined' && el) {{
                        var content = ace.edit(el).getValue();
                        htag_event('{self.ace_editor.id}', 'save', {{target: {{value: content}}}});
                    }} else {{
                        console.error("Cannot save: Ace or element not ready");
                    }}
                }})();
            """)

    def _on_editor_save(self, event):
        # This is a custom event handler triggered by the JS above
        content = event.value
        filename = self.current_file.value
        if filename and content is not None:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.notify("File saved successfully!", "success")
            except Exception as e:
                msg = f"Error saving {filename}: {e}"
                print(msg)
                self.notify(msg, "error")
        else:
            self.notify("Save aborted: no file selected", "error")

    def on_mount(self):
        # We don't auto-load any file now, as per user request
        pass

if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(App).run(reload=False)
