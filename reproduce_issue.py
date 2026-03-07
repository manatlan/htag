from htag import Tag, State, ChromeApp
import time

class App(Tag.App):
    def init(self):
        self.s = State(["A"])
        with self:
            Tag.button("Add (set)", _onclick=self.add_set)
            Tag.button("Add (+=)", _onclick=self.add_iadd)
            Tag.div(lambda: f"List: {self.s.value}")
            Tag.div(lambda: f"Time: {time.time()}")

    def add_set(self, ev):
        self.s.set(self.s.value + ["B"])
        
    def add_iadd(self, ev):
        self.s.value += ["C"]

if __name__ == "__main__":
    ChromeApp(App).run()
