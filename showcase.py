from htag import Tag, ChromeApp, State, prevent, stop
import logging
import time
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)

class FeatureSection(Tag.div):
    """
    Styled component for each test category.
    Demonstrates: Scoped Styles, compact layout.
    """
    styles = """
    & {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 0.8rem;
        border: 1px solid #e2e8f0;
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        min-height: 120px;
    }
    & h3 {
        margin: 0;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.3rem;
    }
    .demo-box {
        padding: 0.4rem;
        background: #f1f5f9;
        border-radius: 6px;
        font-size: 0.75rem;
        border: 1px dashed #cbd5e1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-height: 1.2rem;
    }
    .active {
        background: #dcfce7;
        border-color: #86efac;
        color: #166534;
    }
    button {
        background: #6366f1;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.7rem;
        transition: all 0.2s;
    }
    button:hover { background: #4f46e5; transform: translateY(-1px); }
    button.alt { background: #10b981; }
    button.alt:hover { background: #059669; }
    button.danger { background: #ef4444; }
    button.danger:hover { background: #dc2626; }
    
    .actions { display: flex; gap: 4px; flex-wrap: wrap; }
    input { width: 100%; font-size: 0.75rem; padding: 2px; border: 1px solid #e2e8f0; border-radius: 4px; }
    """
    def init(self, title):
        self <= Tag.h3(title)

class Showcase(Tag.App):
    statics = [
        Tag.style("""
            body { 
                background: #f8fafc; 
                margin: 0; 
                padding: 0.5rem; 
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                color: #1e293b;
                overflow: hidden;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.8rem;
                max-width: 1000px;
                margin: 10px auto;
            }
            @media (max-width: 800px) { .grid { grid-template-columns: repeat(2, 1fr); } }
            @media (max-width: 500px) { .grid { grid-template-columns: 1fr; } }
            
            header { text-align: center; margin-bottom: 0.3rem; }
            header h1 { margin: 0; font-size: 1.2rem; color: #1e293b; }
            header p { margin: 0; color: #64748b; font-size: 0.75rem; }
            
            footer { margin-top: 0.3rem; text-align: center; font-size: 0.7rem; color: #94a3b8; }
        """)
    ]

    def init(self):
        with Tag.header():
            Tag.h1("htag Showcase")
            Tag.p("Ultimate Feature Validation Suite")

        with Tag.div(_class="grid"):
            # 1. State & Mutation
            self.counter = State(0)
            self.items = State(["A"])
            with FeatureSection("1. Reactivity"):
                Tag.div(lambda: f"Count: {self.counter} | Items: {','.join(self.items)}", _class="demo-box")
                with Tag.div(_class="actions"):
                    Tag.button("+1", _onclick=lambda e: self.counter.set(self.counter.value + 1))
                    Tag.button("Mutate", _onclick=lambda e: self.items.append("X"), _class="alt")

            # 2. Async Stepping (Yield)
            with FeatureSection("2. Stepping (Yield)"):
                self.step_label = Tag.div("Ready", _class="demo-box")
                Tag.button("Start Async Process", _onclick=self.stepper)

            # 3. Input Auto-Binding & Toggle Class
            with FeatureSection("3. Binding & Class"):
                self.val = State("Edit me")
                box = Tag.div(lambda: f"Live: {self.val}", _class="demo-box")
                Tag.input(_value=self.val.value, _oninput=lambda e: self.val.set(e.value))
                def toggle(e): box.toggle_class("active")
                Tag.button("Toggle State", _onclick=toggle, _class="alt")

            # 4. Tree & Dict
            with FeatureSection("4. Tree & Dict"):
                # Use a custom ID for find_tag validation
                self.info_box = Tag.div(f"Root: <{self.tag}>", _class="demo-box", _id="custom-info-id")
                def refresh(e): 
                    target = self.find_tag(self, "custom-info-id")
                    if target:
                        target.text = f"Found! Childs: {len(self.childs)}"
                        target["style"] = "border-left: 5px solid #6366f1;"
                Tag.button("Find & Update", _onclick=refresh)

            # 5. Events & Context
            with FeatureSection("5. Events & Context"):
                self.coords = Tag.span() 
                Tag.div("Pos: ", self.coords, _class="demo-box")
                with Tag.div(_class="actions"):
                    @stop
                    def s(e): self.coords.text = f"{e.pageX}, {e.pageY}"
                    with Tag.div(_onclick="alert('Parent')", _style="background:#f1f5f9;padding:2px;border-radius:4px"):
                        Tag.button("Stop & Coords", _onclick=s)
                    
                    def show_ua(e):
                        ua = self.request.headers.get("user-agent", "Unknown")[:15] + "..."
                        self.call_js(f"alert('UA: {ua}')")
                    Tag.button("UA", _onclick=show_ua, _class="alt")
                    
                    @prevent
                    def p(e): self.call_js("console.log('Prevented')")
                    Tag.a("Prevent", _href="https://google.com", _onclick=p, _style="font-size:0.6rem")

            # 6. Global Navigation
            with FeatureSection("6. Hash Nav"):
                self.h = Tag.div("Hash: -", _class="demo-box")
                with Tag.div(_class="actions"):
                    Tag.a("#Home", _href="#Home")
                    Tag.a("#Settings", _href="#Settings")
                self["onhashchange"] = self.on_hash_change

            # 7. Error Handling
            with FeatureSection("7. Errors"):
                self.crash = State(False)
                def rr():
                    if self.crash.value: raise ValueError("Render Crash")
                    return Tag.span("System Stable", _style="color:green;font-size:0.7rem")
                Tag.div(rr, _class="demo-box")
                with Tag.div(_class="actions"):
                    Tag.button("Py", _onclick=lambda e: 1/0, _class="danger")
                    Tag.button("JS", _onclick="err()", _class="danger")
                    Tag.button("Render", _onclick=lambda e: setattr(self.crash, 'value', True), _class="danger")
                    Tag.button("Reset", _onclick=lambda e: setattr(self.crash, 'value', False))

            # 8. Safe Playground
            with FeatureSection("8. Playground"):
                self.pg = Tag.div(_class="demo-box")
                def restore_pg(e=None):
                    self.target = Tag.div("Target Element", _style="color:#6366f1")
                    self.pg.clear().add(self.target)
                restore_pg()
                with Tag.div(_class="actions"):
                    Tag.button("Add", _onclick=lambda e: self.target.add(" • "), _class="alt")
                    Tag.button("Clear", _onclick=lambda e: self.target.clear(), _class="danger")
                    Tag.button("Remove", _onclick=lambda e: self.target.remove(), _class="danger")
                    Tag.button("Restore", _onclick=restore_pg, _class="alt")

            # 9. Lifecycle
            class LifecycleComp(Tag.div):
                def on_mount(self): self.text = "Mounted: " + time.strftime("%M:%S")
            with FeatureSection("9. Lifecycle"):
                self.lc = Tag.div(_class="demo-box")
                with Tag.div(_class="actions"):
                    Tag.button("Mount", _onclick=lambda e: self.lc.add(LifecycleComp()), _class="alt")
                    Tag.button("Unmount", _onclick=lambda e: self.lc.clear(), _class="danger")

            # 10. Transport
            with FeatureSection("10. Transport"):
                self.ts = Tag.div("WebSocket active", _class="demo-box")
                def force_sse(e):
                    self.exit_on_disconnect = False  # Prevent server exit during test
                    self.ts.text = "SSE Mode (Forced)"
                    self.ts.add_class("active")
                    self.call_js("if(window.ws) window.ws.close(); window.fallback();")
                Tag.button("Force SSE Fallback", _onclick=force_sse, _class="danger")

        with Tag.footer():
            Tag.p("htag exhaustive validation • Shared App Instance aware")

    async def stepper(self, e):
        """Demonstrates: Async Generator (Yield)."""
        self.step_label.text = "Step 1: Init..."
        yield 
        await asyncio.sleep(0.5)
        self.step_label.text = "Step 2: Processing..."
        yield
        await asyncio.sleep(0.5)
        self.step_label.text = "Step 3: DONE!"

    def on_hash_change(self, e):
        self.h.text = "Hash: " + (e.newURL.split("#")[-1] if "#" in e.newURL else "-")

if __name__ == "__main__":
    ChromeApp(Showcase).run(reload=True)
