import logging
import asyncio
from htag import Tag, ChromeApp, State

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tailwind-demo")

# ====================================================================
# COMPS : Reusable UI Components based on Tailwind CSS
# ====================================================================

class Button(Tag.button):
    """A reusable button component with Tailwind styling."""
    def init(self, label, variant="primary", **kwargs):
        self <= label
        
        # Base styles for all buttons
        base_classes = "px-4 py-2 rounded-lg font-medium transition-colors duration-200 shadow-sm"
        
        # Variant-specific styles
        if variant == "primary":
            self._class = f"{base_classes} bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800"
        elif variant == "secondary":
            self._class = f"{base_classes} bg-slate-200 text-slate-800 hover:bg-slate-300 active:bg-slate-400"
        elif variant == "danger":
            self._class = f"{base_classes} bg-red-600 text-white hover:bg-red-700 active:bg-red-800"
        else:
            self._class = base_classes
            
        # Allow overriding/adding classes via kwargs if needed
        if "_class" in kwargs:
            self._class += f" {kwargs['_class']}"

class Card(Tag.div):
    """A reusable card container component."""
    def init(self, title=None, **kwargs):
        # 1. Initialize logic/styles
        self._class = "bg-white rounded-xl shadow-md border border-slate-100 overflow-hidden"
        if "_class" in kwargs:
             self._class += f" {kwargs['_class']}"

        # 2. Create body FIRST (so it's available for auto-adding children)
        self.body = Tag.div(_class="p-6")
        Tag.div.add(self, self.body)

        # 3. Add header if needed
        if title:
            header = Tag.div(title, _class="px-6 py-4 border-b border-slate-100 font-semibold text-lg text-slate-800 bg-slate-50")
            # Explicitly add to self (Card), not body (via override add)
            Tag.div.add(self, header)
            # Re-ensure body is after header in child list
            self.body.remove()
            Tag.div.add(self, self.body)

    # Override the default append behavior to add to the card body instead of the main wrapper
    def add(self, o):
         if not hasattr(self, "body"):
             # During initialization, if body isn't ready, fallback to normal add
             return Tag.div.add(self, o)
         self.body <= o

class Badge(Tag.span):
    """A small pill badge for status or counts."""
    def init(self, text, color="blue", **kwargs):
        self <= text
        self._class = f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-{color}-100 text-{color}-800"

class Alert(Tag.div):
    """An alert banner component."""
    def init(self, message, variant="info", **kwargs):
        if variant == "info":
            self._class = "p-4 mb-4 text-sm text-blue-800 rounded-lg bg-blue-50 border border-blue-200"
        elif variant == "success":
            self._class = "p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50 border border-green-200"
        elif variant == "warning":
            self._class = "p-4 mb-4 text-sm text-yellow-800 rounded-lg bg-yellow-50 border border-yellow-200"
        elif variant == "error":
            self._class = "p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 border border-red-200"
            
        if "_class" in kwargs:
            self._class += f" {kwargs['_class']}"
            
        self <= message

class Toast(Tag.div):
    """A client-side self-closing toast component."""
    def init(self, message, variant="info", **kwargs):
       
        
        # Mapping variants to Tailwind colors
        colors = {
            "success": "text-green-800 bg-green-50 border-green-200",
            "error": "text-red-800 bg-red-50 border-red-200",
            "warning": "text-yellow-800 bg-yellow-50 border-yellow-200",
            "info": "text-blue-800 bg-blue-50 border-blue-200"
        }
        variant_classes = colors.get(variant, colors["info"])
        
        # Initial classes (invisible and translated)
        self._class = f"p-4 mb-4 text-sm rounded-lg border shadow-xl transform transition-all duration-300 translate-y-2 opacity-0 {variant_classes}"
        self <= message
        
        # Self-contained JS for animations and removal (using call_js for execution)
        self.call_js("""
            var el = document.getElementById('%s');
            if(el) {
                // Animate in
                setTimeout(() => {
                    el.classList.remove('translate-y-2', 'opacity-0');
                    el.classList.add('translate-y-0', 'opacity-100');
                }, 10);

                // Animate out and remove
                setTimeout(() => {
                    el.classList.remove('translate-y-0', 'opacity-100');
                    el.classList.add('translate-y-2', 'opacity-0');
                    setTimeout(() => el.remove(), 300);
                }, 3000);
            }
        """ % self.id)

class Modal(Tag.div):
    """A full-screen modal dialog component."""
    def init(self, title, content, **kwargs):
        self._class = "fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black bg-opacity-50"
        self._style = "display: none;"
        self._onclick = self.hide # Close on overlay click
        
        # The dialog box (prevent closing when clicking inside)
        self.dialog = Tag.div(_class="bg-white rounded-xl shadow-2xl max-w-lg w-full", _onclick="event.stopPropagation()")
        
        # Header
        header = Tag.div(_class="flex items-center justify-between p-4 border-b")
        header <= Tag.h3(title, _class="text-xl font-semibold text-gray-900")
        
        close_btn = Tag.button(_class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center")
        close_btn._onclick = self.hide
        close_btn <= Tag.span("×", _class="text-2xl leading-none")
        header <= close_btn
        
        self.dialog <= header
        
        # Content
        body = Tag.div(_class="p-6")
        body <= content
        self.dialog <= body
        
        self <= self.dialog

    def show(self, event=None):
        self._style = "display: flex;"

    def hide(self, event=None):
        self._style = "display: none;"

class Input(Tag.input):
    """A styled text input component."""
    def init(self, placeholder="", **kwargs):
        self._type = "text"
        self._placeholder = placeholder
        self._class = "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 outline-none transition-colors"
        if "_class" in kwargs:
             self._class += f" {kwargs['_class']}"

class Toggle(Tag.label):
    """A modern toggle switch component."""
    def init(self, label_text, **kwargs):
        # Extract the onchange event from kwargs for the inner checkbox if it exists
        onchange = kwargs.pop("_onchange", kwargs.pop("onchange", None))
        
        self._class = "relative inline-flex items-center cursor-pointer"
        
        # The hidden checkbox is what stores the state
        # In htag, an input automatically updates its `value` attribute on client changes
        self.checkbox = Tag.input(_type="checkbox", _class="sr-only peer")
        if onchange:
             self.checkbox._onchange = onchange
        self <= self.checkbox
        
        # The visual toggle
        slider = Tag.div(_class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600")
        self <= slider
        
        if label_text:
            self <= Tag.span(label_text, _class="ml-3 text-sm font-medium text-gray-900")

    @property
    def value(self):
        # We read the 'checked' state from the underlying input checkbox
        # htag stores synced values in _attrs (accessed via _value)
        return getattr(self.checkbox, "_value", False) == True

class Table(Tag.div):
    """A responsive table component."""
    def init(self, headers, rows, **kwargs):
        self._class = "relative overflow-x-auto shadow-md sm:rounded-lg"
        if "_class" in kwargs:
             self._class += f" {kwargs['_class']}"
             
        table = Tag.table(_class="w-full text-sm text-left text-gray-500")
        self <= table
        
        # Header
        thead = Tag.thead(_class="text-xs text-gray-700 uppercase bg-gray-50")
        tr_head = Tag.tr()
        for h in headers:
            tr_head <= Tag.th(h, _class="px-6 py-3", scope="col")
        thead <= tr_head
        table <= thead
        
        # Body
        tbody = Tag.tbody()
        for i, row in enumerate(rows):
            # Alternating row colors
            bg_class = "bg-white border-b" if i % 2 == 0 else "bg-gray-50 border-b"
            tr = Tag.tr(_class=f"{bg_class} hover:bg-gray-100")
            
            for j, cell in enumerate(row):
                if j == 0:
                     # First column usually highlighted
                     tr <= Tag.th(cell, _class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap", scope="row")
                else:
                     tr <= Tag.td(cell, _class="px-6 py-4")
            tbody <= tr
        table <= tbody

class ProgressBar(Tag.div):
    """A simple progress bar component."""
    def init(self, progress=0, color="blue", **kwargs):
        self._class = "w-full bg-gray-200 rounded-full h-2.5 mb-4 dark:bg-gray-700"
        
        # Internal div for the bar itself, with reactive width
        Tag.div(
            _class=f"bg-{color}-600 h-2.5 rounded-full transition-all duration-300", 
            _style=lambda: f"width: {self._eval_child(progress)}%"
        )


class CodeBlock(Tag.div):
    """A styled container to display code snippets."""
    def init(self, code, language="python", **kwargs):
        self._class = "rounded-md bg-slate-800 p-4 overflow-x-auto text-sm text-slate-50 font-mono shadow-inner border border-slate-700"
        if "_class" in kwargs:
             self._class += f" {kwargs['_class']}"
             
        pre = Tag.pre()
        code_tag = Tag.code(code, _class=f"language-{language}")
        pre <= code_tag
        self <= pre

class Spinner(Tag.div):
    """A loading spinner component."""
    def init(self, size="md", color="blue", **kwargs):
        
        # Mapping sizes to Tailwind classes
        sizes = {
            "sm": "w-4 h-4 text-xs mt-1",
            "md": "w-8 h-8",
            "lg": "w-12 h-12"
        }
        sz_class = sizes.get(size, sizes["md"])
        
        # We start by making the container a flex center block if we want, or inline. 
        # But we'll just style the spinner SVG directly.
        
        self._class = "flex justify-center items-center"
        if "_class" in kwargs:
             self._class += f" {kwargs['_class']}"
             
        # Create an animated SVG for the spinner
        svg = Tag.svg(
            Tag.circle(_class="opacity-25", _cx="12", _cy="12", _r="10", _stroke="currentColor", _stroke_width="4"),
            Tag.path(_class="opacity-75", _fill="currentColor", _d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"),
            _class=f"animate-spin {sz_class} text-{color}-600", _xmlns="http://www.w3.org/2000/svg", _fill="none", _viewBox="0 0 24 24"
        )
        self <= svg

class Accordion(Tag.div):
    """A collapsible accordion item."""
    def init(self, title, content, is_open=False, **kwargs):
        self.is_open = is_open
        self._class = "border border-gray-200 rounded-lg mb-2 overflow-hidden"
        
        # Header / Button
        self.header = Tag.button(_type="button", _onclick=self.toggle, _class="flex items-center justify-between w-full p-5 font-medium text-left text-gray-500 bg-gray-50 hover:bg-gray-100 transition-colors bg-white")
        self.header <= Tag.span(title)
        
        # Arrow SVG wrapper
        self.arrow = Tag.svg(
            Tag.path(_stroke="currentColor", _stroke_linecap="round", _stroke_linejoin="round", _stroke_width="2", _d="M9 5 5 1 1 5"),
            _data_accordion_icon="", _class="w-3 h-3 rotate-180 shrink-0", _aria_hidden="true", _xmlns="http://www.w3.org/2000/svg", _fill="none", _viewBox="0 0 10 6"
        )
        
        # Store a ref so we can rotate the arrow class later
        self.arrow_wrapper = Tag.span(self.arrow, _class=f"transition-transform duration-200 {'rotate-180' if self.is_open else ''}")
        self.header <= self.arrow_wrapper
        self <= self.header
        
        # Body
        self.body = Tag.div(_class="p-5 border-t border-gray-200")
        
        if isinstance(content, Tag.tag):
            self.body <= content
        else:
            self.body <= Tag.p(str(content), _class="mb-2 text-gray-500")
            
        # Wrap body in a div that toggles display
        self.body_wrapper = Tag.div(self.body, _class=f"{'' if self.is_open else 'hidden'}")
        self <= self.body_wrapper

    def toggle(self, event):
        self.is_open = not self.is_open
        self.body_wrapper.toggle_class("hidden")
        self.arrow_wrapper.toggle_class("rotate-180")


class MessageBox(Tag.div):
    """A modal dialog component."""
    def init(self, title, message, on_close=None, type="info", **kwargs):
        self.on_close = on_close
        
        # Type styling
        icon_bg = "bg-blue-100 text-blue-600"
        btn_class = "bg-blue-600 hover:bg-blue-700 focus:ring-blue-300"
        if type == "danger" or type == "error":
            icon_bg = "bg-red-100 text-red-600"
            btn_class = "bg-red-600 hover:bg-red-800 focus:ring-red-300"
            icon_svg = Tag.svg(
                Tag.path(_fill_rule="evenodd", _d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z", _clip_rule="evenodd"),
                _aria_hidden="true", _class="w-6 h-6", _fill="currentColor", _viewBox="0 0 20 20", _xmlns="http://www.w3.org/2000/svg"
            )
        elif type == "success":
            icon_bg = "bg-green-100 text-green-600"
            btn_class = "bg-green-600 hover:bg-green-800 focus:ring-green-300"
            icon_svg = Tag.svg(
                Tag.path(_fill_rule="evenodd", _d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z", _clip_rule="evenodd"),
                _aria_hidden="true", _class="w-6 h-6", _fill="currentColor", _viewBox="0 0 20 20", _xmlns="http://www.w3.org/2000/svg"
            )
        else:
            icon_svg = Tag.svg(
                Tag.path(_fill_rule="evenodd", _d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z", _clip_rule="evenodd"),
                _aria_hidden="true", _class="w-6 h-6", _fill="currentColor", _viewBox="0 0 20 20", _xmlns="http://www.w3.org/2000/svg"
            )
        # Modal backdrop (fixed full screen, gray overlay with opacity, flex centering)
        # We start hidden: display: none
        self._class = "fixed inset-0 z-[100] flex items-center justify-center overflow-x-hidden overflow-y-auto outline-none focus:outline-none bg-gray-900 bg-opacity-50"
        self._style = "display: none;"
        self._onclick = self.close_modal
        
        # Modal Dialog Core
        dialog = Tag.div(_class="relative w-full max-w-md p-4 md:h-auto", _onclick="event.stopPropagation()")
        self <= dialog
        
        # Modal Content
        content = Tag.div(_class="relative bg-white rounded-lg shadow-xl")
        dialog <= content
        
        # Close 'X' button in top right
        close_btn = Tag.button(_type="button", _onclick=self.close_modal, _class="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center")
        close_btn <= Tag.span("✖", _class="w-5 h-5 text-xl leading-none")
        content += close_btn
        
        # Body (Icon + Text)
        body = Tag.div(_class="p-6 text-center")
        icon_container = Tag.div(icon_svg, _class=f"mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full {icon_bg}")
        body <= icon_container
        body <= Tag.h3(title, _class="mb-2 text-lg font-normal text-gray-500")
        body <= Tag.p(message, _class="text-sm text-gray-500 mb-6")
        
        # Action Buttons
        ok_btn = Tag.button("OK", _type="button", _onclick=self.close_modal, _class=f"text-white focus:ring-4 focus:outline-none font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center mr-2 {btn_class}")
        body <= ok_btn
        
        content += body
        
    def open_modal(self, event=None):
        self._style = "display: flex;"
        
    def close_modal(self, event=None):
        self._style = "display: none;"
        if self.on_close:
            self.on_close()

class Tabs(Tag.div):
    """A tabbed layout component."""
    def init(self, tabs_dict, **kwargs):
        self._class = "w-full"
        self.tabs_dict = tabs_dict
        self.active_tab = list(tabs_dict.keys())[0] if tabs_dict else None
        self.render_tabs()

    def render_tabs(self):
        self.clear()
        
        # Header sequence
        header = Tag.ul(_class="flex flex-wrap text-sm font-medium text-center text-gray-500 border-b border-gray-200")
        for title in self.tabs_dict.keys():
            is_active = (title == self.active_tab)
            li = Tag.li(_class="mr-2")
            
            # Closure block for the click handler
            def make_handler(t):
                return lambda e: self.select_tab(t)
                
            a_class = "inline-block p-4 text-blue-600 bg-blue-50 rounded-t-lg active font-semibold" if is_active else "inline-block p-4 rounded-t-lg hover:text-gray-600 hover:bg-gray-50 cursor-pointer"
            
            li <= Tag.a(title, _class=a_class, _onclick=make_handler(title))
            header <= li
        self <= header
        
        # Body panel
        if self.active_tab:
            body = Tag.div(_class="p-6 bg-white rounded-b-lg border border-t-0 border-gray-200")
            content = self.tabs_dict[self.active_tab]
            
            # Allow strings or Tag instances
            if hasattr(content, "tag"):
                body <= content
            else:
                body <= Tag.p(str(content), _class="text-gray-600")
            self <= body

    def select_tab(self, title):
        self.active_tab = title
        self.render_tabs()

class Dropdown(Tag.div):
    """A floating dropdown menu component."""
    def init(self, title, items, **kwargs):

        self._class = "relative inline-block text-left"
        if "_class" in kwargs: self._class += f" {kwargs['_class']}"
        self.is_open = False
        self.items = items
        
        # Button
        self.btn = Button(title, variant="secondary", _onclick=self.toggle)
        self.btn <= Tag.svg(Tag.path(_stroke="currentColor", _stroke_linecap="round", _stroke_linejoin="round", _stroke_width="2", _d="m1 1 4 4 4-4"), _class="w-2.5 h-2.5 ml-2.5 inline", _aria_hidden="true", _xmlns="http://www.w3.org/2000/svg", _fill="none", _viewBox="0 0 10 6")
        self <= self.btn
        
        # Menu panel
        self.menu = Tag.div(_class="absolute left-0 z-10 mt-2 w-44 origin-top-left rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 transition-all duration-200")
        self <= self.menu
        self.update_menu()

    def toggle(self, e):
        self.is_open = not self.is_open
        self.update_menu()

    def update_menu(self):
        self.menu.clear()
        if self.is_open:
            self.menu._class = "absolute left-0 z-10 mt-2 w-44 origin-top-left rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 opacity-100 scale-100"
            py_items = Tag.div(_class="py-1")
            for label, callback in self.items:
                def make_cb(cb):
                    def handler(e):
                        self.is_open = False
                        self.update_menu()
                        if cb: return cb(e)
                    return handler
                
                # We use a pure div button-like structure so it doesn't navigate
                py_items <= Tag.div(label, _class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer", _onclick=make_cb(callback))
            self.menu <= py_items
        else:
            self.menu._class = "absolute left-0 z-10 mt-2 w-44 origin-top-left rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 opacity-0 scale-95 pointer-events-none"




# ====================================================================
# APP : Main Application Flow
# ====================================================================

class DemoApp(Tag.App):
    # Using Tailwind Play CDN for prototyping (In production, you'd use a compiled CSS file)
    statics = [
        Tag.script(_src="https://cdn.tailwindcss.com"),
        Tag.style("body { background-color: #f8fafc; }") # Light slate background for the whole page
    ]

    def init(self):
        # 1. State Initialization
        self.count = State(0)
        self.user_name = State("")
        self.dark_mode = State(False)
        self.progress = State(30)
        self.is_loading = State(False)

        # 2. Declarative Layout (Zero-Boilerplate)
        with Tag.div(_class="min-h-screen p-8 flex flex-col items-center justify-center"):
            
            with Tag.div(_class="text-center mb-10"):
                Tag.h1("Tailwind Components Demo", _class="text-4xl font-extrabold text-slate-900 tracking-tight")
                Tag.p("htag + Tailwind CSS in action", _class="mt-2 text-lg text-slate-600")

            # Create a Grid for our Cards
            with Tag.div(_class="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-4xl"):
                
                # --- Card 1: Counter Example ---
                with Card(title="Counter Example"):
                    # Reactive Counter Display
                    Tag.div(
                        lambda: str(self.count.value), 
                        _class=lambda: "text-5xl font-bold text-center mb-6 " + (
                            "text-red-600" if self.count.value < 0 else 
                            "text-green-600" if self.count.value > 0 else 
                            "text-blue-600"
                        )
                    )
                    
                    with Tag.div(_class="flex justify-center gap-4"):
                        Button("-1", variant="secondary", _onclick=lambda e: self.count.set(self.count.value - 1))
                        Button("+1", variant="primary", _onclick=lambda e: self.count.set(self.count.value + 1))
                        Button("Reset", variant="danger", _onclick=lambda e: self.count.set(0))

                # --- Card 2: Status Indicators ---
                with Card(title="Status Indicators"):
                    Tag.p("This card demonstrates reusable non-interactive elements.", _class="text-slate-600 mb-4")
                    with Tag.div(_class="flex flex-wrap gap-2 mb-6"):
                        Badge("New", "green")
                        Badge("Processing", "yellow")
                        Badge("Error", "red")
                        Badge("v1.2.0", "blue")
                    Button("Acknowledge", variant="primary", _class="w-full", _onclick=lambda e: e.target.call_js("alert('Acknowledged!')"))
                
                # --- Card 3: Interactive Forms ---
                with Card(title="Interactive Elements", _class="md:col-span-1 border-t-4 border-t-purple-500"):
                    with Tag.div(_class="flex flex-col gap-6"):
                        # Text input example
                        with Tag.div(_class="flex flex-col gap-2"):
                            Tag.label("Your Name", _class="text-sm font-medium text-gray-700")
                            Input(placeholder="Type your name...", _oninput=lambda e: self.user_name.set(e.value))
                            # Hello message is purely reactive
                            Tag.div(
                                lambda: f"Hello, {self.user_name.value}!" if self.user_name.value else "Hello, stranger!",
                                _class=lambda: "text-sm mt-1 " + ("text-blue-600 font-medium" if self.user_name.value else "text-gray-500")
                            )
                        
                        # Toggle example
                        with Tag.div(_class="flex items-center justify-between mt-2 pt-4 border-t border-gray-100"):
                            Toggle("Enable Dark Text", _onchange=lambda e: self.dark_mode.set(e.target.value))
                        
                        # Alert area is reactive to the toggle
                        Tag.div(lambda: 
                            Alert("Feature activated! This would normally switch themes.", variant="success") if self.dark_mode.value else 
                            Alert("Feature disabled. Back to normal.", variant="warning")
                        )

                # --- Card 4: Table Data ---
                with Card(title="Data Table", _class="md:col-span-2"):
                    Table(
                        headers = ["Nom", "Rôle", "Statut", "Action"],
                        rows = [
                            ["Alice Dupont", "Admin", Badge("Actif", "green"), Button("Editer", "secondary", _class="text-xs py-1 px-2", _onclick=lambda e: self.fire_toast("Edition de Alice Dupont...", "info"))],
                            ["Bob Martin", "User", Badge("Inactif", "gray"), Button("Editer", "secondary", _class="text-xs py-1 px-2", _onclick=lambda e: self.fire_toast("Edition de Bob Martin...", "info"))],
                            ["Charlie", "Editor", Badge("Review", "yellow"), Button("Editer", "secondary", _class="text-xs py-1 px-2", _onclick=lambda e: self.fire_toast("Edition de Charlie...", "info"))]
                        ]
                    )

                # --- Card 5: Modals ---
                with Card(title="Modals & Dialogs", _class="md:col-span-2"):
                    with Tag.div(_class="flex gap-4 p-4 items-center justify-center"):
                        Button("Show Info Modal", "primary", _onclick=lambda e: self.info_modal.open_modal())
                        Button("Show Danger Modal", "danger", _onclick=lambda e: self.danger_modal.open_modal())
                        Button("Show Advanced Modal", "info", _onclick=lambda e: self.advanced_modal.show())

                # --- Card 6: Utils ---
                with Card(title="Utilities & Feedback", _class="md:col-span-2"):
                    with Tag.div(_class="grid grid-cols-1 md:grid-cols-2 gap-8"):
                        with Tag.div():
                            Tag.h3("Task Progress", _class="text-sm font-semibold text-gray-700 mb-2")
                            # Progress bar is now fully reactive by passing a lambda
                            ProgressBar(progress=lambda: self.progress.value, color="blue")
                            with Tag.div(_class="flex gap-2 mt-4"):
                                Button("+10%", "secondary", _onclick=lambda e: self.progress.set(min(100, self.progress.value + 10)))
                                Button("Reset", "danger", _class="ml-auto", _onclick=lambda e: self.progress.set(0))
                        
                        with Tag.div():
                            Tag.h3("Code Snippet", _class="text-sm font-semibold text-gray-700 mb-2")
                            CodeBlock('def hello_world():\n    print("Hello from htag!")', language="python")

                # --- Card 7: Advanced ---
                with Card(title="Advanced Components", _class="md:col-span-2"):
                    with Tag.div(_class="grid grid-cols-1 md:grid-cols-2 gap-8"):
                        with Tag.div():
                            Tag.h3("Accordions / Expansion Panels", _class="text-sm font-semibold text-gray-700 mb-4")
                            Accordion("What is htag?", "htag is a lightweight, pure Python framework for building modern web applications without writing JavaScript.", is_open=True)
                            Accordion("Why use Tailwind CSS?", "Tailwind allows you to rapidly build custom user interfaces by composing utility classes directly in your markup, keeping CSS files small.")
                        
                        with Tag.div():
                            Tag.h3("Loading States", _class="text-sm font-semibold text-gray-700 mb-4")
                            with Tag.div(_class="flex items-center gap-6 p-4 rounded-lg border border-dashed border-gray-300 bg-gray-50"):
                                Tag.div([Spinner("sm", "red"), Tag.span("Small", _class="text-xs text-gray-500 mt-2 block text-center")])
                                Tag.div([Spinner("md", "blue"), Tag.span("Medium", _class="text-xs text-gray-500 mt-2 block text-center")])
                                Tag.div([Spinner("lg", "green"), Tag.span("Large", _class="text-xs text-gray-500 mt-2 block text-center")])
                            
                            with Button("Save Changes", variant="primary", _class="mt-4 flex items-center justify-center gap-2", 
                                       _disabled=lambda: self.is_loading.value,
                                       _onclick=self.fake_loading) as btn:
                                # Reactive spinner inside button
                                Tag.span(lambda: Spinner("sm", "white") if self.is_loading.value else "")

                # --- Card 8: Tabs & Dropdowns ---
                with Card(title="Navigation & Menus", _class="md:col-span-2 border-t-4 border-t-teal-500"):
                    with Tag.div(_class="grid grid-cols-1 md:grid-cols-2 gap-8"):
                        with Tag.div():
                            Tag.h3("Tabs Panel", _class="text-sm font-semibold text-gray-700 mb-4")
                            Tabs({
                                "Profil": Tag.div([Tag.h4("Profil Utilisateur", _class="font-bold mb-2"), Tag.p("Gérez vos informations personnelles ici.", _class="text-sm text-gray-600")]),
                                "Sécurité": Tag.div([Tag.h4("Sécurité", _class="font-bold mb-2"), Tag.p("Paramètres de mot de passe et 2FA.", _class="text-sm text-gray-600")]),
                                "Notifications": "Aucune nouvelle notification pour le moment."
                            })
                        
                        with Tag.div():
                            Tag.h3("Menus & Toasts", _class="text-sm font-semibold text-gray-700 mb-4")
                            Dropdown("Actions Rapides", [
                                ("Déclencher un Toast Succès", lambda e: self.fire_toast("Opération réussie !", "success")),
                                ("Déclencher une Alerte", lambda e: self.fire_toast("Ceci est une erreur importante", "error")),
                                ("Option inerte", None)
                            ])
                            Tag.p("Cliquez sur le dropdown pour déclencher un toast éphémère.", _class="mt-4 text-xs text-gray-500")

            # 3. Floating components
            self.info_modal = MessageBox("Nouvelle Fonctionnalité", "Les boîtes de dialogue modales sont maintenant disponibles !", type="info")
            self.danger_modal = MessageBox("Action Irréversible", "Êtes-vous sûr de vouloir supprimer cet élément ?", type="danger")
            self.advanced_modal = Modal("Composant Modal Avancé", Tag.div([
                Tag.p("Ce modal est plus générique. Vous pouvez y mettre n'importe quel contenu htag.", _class="text-gray-600 mb-4"),
                Button("Fermer ce modal", variant="secondary", _class="mt-6 w-full", _onclick=lambda e: self.advanced_modal.hide())
            ]))
            self.toaster = Tag.div(_class="fixed bottom-5 right-5 z-50 flex flex-col gap-2")

    def fire_toast(self, message, variant="success"):
        self.toaster <= Toast(message, variant)

    async def fake_loading(self, event):
        self.is_loading.set(True)
        yield
        await asyncio.sleep(2)
        self.is_loading.set(False)
        self.fire_toast("Sauvegardé avec succès !")


if __name__ == "__main__":
    ChromeApp(DemoApp, width=1024, height=768).run()
