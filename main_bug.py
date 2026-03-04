import time
from htag import Tag, State

# hi2 !!

class App(Tag.App):
    def init(self):
        self <= Tag.button("Trigger Python Error", _class="btn", _onclick=self.trigger_py_error)
        self <= Tag.button("Trigger JS Error", _class="btn", _onclick="not_defined_function()")
        self <= Tag.button("Trigger Async Python Error", _class="btn", _onclick=self.trigger_async_error)
        self <= Tag.button("Trigger Render Error", _class="btn", _onclick=self.trigger_render_error)
        
        self.should_crash = State(False)
        
        def crashing_render():
            if self.should_crash.value:
                # This will cause a crash during the component re-rendering phase
                raise TypeError("This component crashed while rendering!")
            return ""
            
        self <= crashing_render
            
    def trigger_py_error(self, event):
        raise ValueError("This is a deliberate Python backend error!")
        
    async def trigger_async_error(self, event):
        yield
        time.sleep(1) # Simulate some work
        raise RuntimeError("Async work failed!")
        
    def trigger_render_error(self, event):
        self.should_crash.value = True

if __name__ == "__main__":
    from htag import ChromeApp
    # ChromeApp(App) forces debug=True by default. 
    ChromeApp(App).run()
