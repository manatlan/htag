# -*- coding: utf-8 -*-
from htag import Tag
"""
this code could be a good start for the future "htag.ui" module

it should be KISS and respect shoelace/htag components on all best practices.

The current toast is still broken ;-(
"""
class ui_App(Tag.App):
    """
    Base class for UI applications.
    Handles dependencies, the design system, and FOUC prevention.
    """
    statics = [
        # Design System (Shoelace)
        Tag.link(_rel="stylesheet", _href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.19.1/cdn/themes/light.css"),
        Tag.link(_rel="stylesheet", _href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.19.1/cdn/themes/dark.css"),
        Tag.script(_type="module", _src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.19.1/cdn/shoelace-autoloader.js"),
        # FOUC prevention
        Tag.style(":not(:defined) { visibility: hidden; }"),
        # Global Styles using Design Tokens
        Tag.style("""
            body { 
                background-color: var(--sl-color-neutral-0);
                color: var(--sl-color-neutral-900);
                display: flex; justify-content: center; align-items: center; 
                height: 100vh; margin: 0; 
                font-family: var(--sl-font-sans);
            }
            
            /* Tabs fill height utility */
            sl-tab-group.fill-height { display: flex; flex-direction: column; height: 100%; }
            sl-tab-group.fill-height::part(base) { display: flex; flex-direction: column; flex: 1; }
            sl-tab-group.fill-height::part(body) { flex: 1; overflow: auto; }
        """)
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_class("sl-theme-light")

class ui_Title(Tag.h1):
    def init(self, text, **kwargs):
        super().init(text, **kwargs)
        self._style = "margin:0; font-size: var(--sl-font-size-large); font-weight: var(--sl-font-weight-bold); color: var(--sl-color-neutral-900);"

class ui_Text(Tag.div):
    def init(self, text, **kwargs):
        super().init(text, **kwargs)
        self._style = "color: var(--sl-color-neutral-600); line-height: var(--sl-line-height-normal);"

class ui_Icon(Tag.sl_icon):
    def init(self, name, **kwargs):
        self._name = name
        super().init(**kwargs)
        self._style = "color: inherit; font-size: inherit;"

class ui_IconButton(Tag.sl_icon_button):
    def init(self, name, **kwargs):
        self._name = name
        super().init(**kwargs)
        self._style = "color: var(--sl-color-neutral-600); font-size: 1.25rem;"

class ui_Badge(Tag.sl_badge):
    def init(self, text, variant="primary", **kwargs):
        self._variant = variant
        super().init(text, **kwargs)

class ui_Button(Tag.sl_button):
    def init(self, text, **kwargs):
        self._variant = kwargs.pop("_variant", "default")
        onclick = kwargs.pop("_onclick", None)
        super().init(text, **kwargs)
        if onclick:
            self._onclick = onclick

class ui_Checkbox(Tag.sl_checkbox):
    def init(self, text, **kwargs):
        onchange = kwargs.pop("_onchange", None)
        super().init(text, **kwargs)
        if onchange:
            self._user_onchange = onchange
            # Manually bind the Shoelace 'sl-change' event to an htag callback
            # passing the 'this.checked' boolean value directly
            self.call_js(f"this.addEventListener('sl-change', (e) => {{ {self.bind._internal_change(b'this.checked')} }})")

    def _internal_change(self, is_checked):
        # We receive the boolean directly because we passed b'this.checked'
        self["checked"] = is_checked
        # Call the user callback
        if hasattr(self, "_user_onchange") and self._user_onchange:
            # We construct a fake event dict to maintain signature compatibility
            mock_event = type('MockEvent', (), {'target': self, 'args': [is_checked]})()
            self._user_onchange(mock_event)


class ui_Dialog(Tag.sl_dialog):
    def init(self, title, **kwargs):
        self._label = title
        super().init(**kwargs)
    def show(self):
        self._open = True
    def hide(self):
        self._open = False

class ui_Drawer(Tag.sl_drawer):
    def init(self, title, **kwargs):
        self._label = title
        super().init(**kwargs)
    def show(self):
        self._open = True
    def hide(self):
        self._open = False

class ui_Spinner(Tag.sl_spinner):
    def init(self, **kwargs):
        super().init(**kwargs)

def ui_Toast(caller: Tag, text: str, variant: str = "primary", duration: int = 3000):
    """
    KISS implementation of a Shoelace Toast.
    Toasts are ephemeral and do not belong in the htag state tree.
    """
    import json
    import html
    icon_name = {
        "primary": "info-circle", "success": "check2-circle", "neutral": "gear", 
        "warning": "exclamation-triangle", "danger": "exclamation-octagon"
    }.get(variant, "info-circle")
    
    # Safely pass the text to JS as a JSON string
    safe_text = json.dumps(html.escape(text))
    
    js = f"""
    const alert = Object.assign(document.createElement('sl-alert'), {{
        variant: '{variant}',
        closable: true,
        duration: {duration},
        innerHTML: `<sl-icon name="{icon_name}" slot="icon"></sl-icon> ` + {safe_text}
    }});
    
    // On le cache temporairement pour éviter qu'il ne s'intègre au 'display: flex' 
    // du body et ne décale toute l'interface avant d'être déplacé dans le toast-stack.
    alert.style.display = 'none';
    document.body.append(alert);
    
    customElements.whenDefined('sl-alert').then(() => {{
        alert.style.display = '';
        setTimeout(() => alert.toast(), 10);
    }});
    """
    caller.call_js(js)

class ui_SplitPanel(Tag.sl_split_panel):
    def init(self, **kwargs):
        super().init(**kwargs)
        # Create persistent slots as children
        self.start = Tag.div(_slot="start", _style="height: 100%; width: 100%; overflow: auto;")
        self.end = Tag.div(_slot="end", _style="height: 100%; width: 100%; overflow: auto; background: var(--sl-color-neutral-0);")
        with self:
            self.start
            self.end

class ui_Card(Tag.sl_card):
    def init(self, title=None, footer=None, **kwargs):
        super().init(**kwargs)
        self._style = "width: 100%; max-width: 400px;"
        if title:
            with self:
                with Tag.div(_slot="header", _style="display: flex; align-items: center; justify-content: space-between;"):
                    ui_Title(title)
                    self.header_actions = Tag.div(_style="display: flex; gap: var(--sl-spacing-x-small);")
                    
        if footer:
            with self:
                Tag.div(footer, _slot="footer")

class ui_Tab(Tag.sl_tab):
    """
    Represents a single tab button in a tab group.
    Must be a direct child of ui_Tabs.
    """
    def init(self, text, panel: str, **kwargs):
        self._panel = panel
        self._slot = "nav"
        super().init(text, **kwargs)

class ui_TabPanel(Tag.sl_tab_panel):
    """
    Represents the panel content for a tab.
    Must be a direct child of ui_Tabs.
    """
    def init(self, name: str, **kwargs):
        self._name = name
        super().init(**kwargs)

class ui_Tabs(Tag.sl_tab_group):
    """
    KISS wrapper around Shoelace tab group.
    Children must be `ui_Tab` and `ui_TabPanel` components.
    """
    def init(self, **kwargs):
        super().init(**kwargs)

class MyApp(ui_App):
    def init(self):
        self.count = 0
        
        # Overlays
        self.dialog = ui_Dialog("Settings")
        with self.dialog:
            ui_Text("Settings panel content.")
            ui_Button("Close", _onclick=lambda e: self.dialog.hide())

        self.drawer = ui_Drawer("System Info")
        with self.drawer:
            ui_Text("Drawer content.")

        # Root Layout: Split Panel
        with ui_SplitPanel(_style="width: 800px; height: 500px; border: solid 1px var(--sl-color-neutral-200);") as sp:
            # Left Side (Start Slot)
            with sp.start:
                with Tag.div(_style="display: flex; align-items: center; justify-content: center; height: 100%;"):
                    with ui_Card(title="Core Controls") as self.card:
                        with self.card.header_actions:
                            ui_IconButton("gear", _onclick=lambda e: self.dialog.show())
                        
                        ui_Text("Status Dashboard")
                        with Tag.div(_style="margin-top: 1rem; display: flex; align-items: center; gap: 0.5rem;"):
                            self.badge = ui_Badge("Standby", variant="neutral")
                        
                        with Tag.div(_slot="footer", _style="display: flex; gap: 0.5rem; align-items: center; justify-content: space-between; width: 100%;"):
                            with Tag.div(_style="display: flex; gap: 0.5rem;"):
                                ui_Button("Increment", _variant="primary", _onclick=self.inc)
                                ui_Button("Info", _onclick=lambda e: self.drawer.show())
                            ui_Checkbox("Dark Mode", _onchange=self.toggle_dark_mode)

            # Right Side (End Slot)
            with sp.end:
                with ui_Tabs(_class="fill-height"):
                    ui_Tab("General", panel="general", active=True)
                    ui_Tab("Advanced", panel="advanced")
                    
                    with ui_TabPanel(name="general", _style="height: 100%;"):
                        with Tag.div(_style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; width: 100%; gap: 1rem; padding: 1rem;"):
                            ui_Spinner(_style="font-size: 3rem;")
                            ui_Text("System Processing...")
                            ui_Button("Notify User", _variant="success", _onclick=self.notify)
                            
                    with ui_TabPanel(name="advanced", _style="height: 100%;"):
                        with Tag.div(_style="padding: 1rem;"):
                            ui_Text("Advanced settings would go here.")

    def inc(self, event):
        self.count += 1
        self.badge.text = f"Activity: {self.count}"
        self.badge._variant = "primary" if self.count < 5 else "success"

    def notify(self, event):
        ui_Toast(self, f"Broadcast: New event recorded ({self.count})", variant="success")

    def toggle_dark_mode(self, event):
        # We know _internal_change sets self["checked"] and passes event with event.args[0]
        try:
            is_dark = bool(event.args[0]) if event.args else False
        except Exception:
            is_dark = False

        # ui_Toast(self, f"Toggling dark mode: {is_dark}")

        if is_dark:
            self.class_name = "sl-theme-dark"  # ui_App defaults to sl-theme-light
            self.call_js("document.documentElement.classList.add('sl-theme-dark');")
        else:
            self.class_name = "sl-theme-light"
            self.call_js("document.documentElement.classList.remove('sl-theme-dark');")

if __name__ == "__main__":
    from htag import ChromeApp
    ChromeApp(MyApp).run(reload=True)
