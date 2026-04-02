from htag import Tag,States,ChromeApp
from time import time
import asyncio

class LifeCycleApp(Tag.App):
    statics = [Tag.title("Life Cycle Demo")]
    def init(self):
        # initial states (executed one time)
        self.states = States(cpt=0, time=0)

    
        with self:        
            # manual update
            Tag.button(self.states.cpt,"+", _onclick=self.on_click)
            
            # task update
            Tag.div( self.states.time )

            # computed
            Tag.div( lambda: f"computed=({self.states.cpt} & {self.states.time})" )


    def on_mount(self):
        # at each mount (at 1st and following F5), this code is executed
        # to mount things
        async def process():
            while 1:
                self.states.time += 1
                await asyncio.sleep(0.5)
        self.task = asyncio.create_task(process())
        
    def on_unmount(self):
        # at each onmount (at end and following F5), this code is executed
        # to unmount things
        self.task.cancel()
    
    def on_click(self, o):
        self.states.cpt += 1


if __name__ == "__main__":
    ChromeApp(LifeCycleApp).run(reload=False)
