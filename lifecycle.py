from htag import Tag,State,ChromeApp
from time import time
import asyncio

class Tutu(Tag.App):
    def init(self):
        # initial states (executed one time)
        self.s_cpt = State(0)
        self.s_time = State( 41 )

        with self:        
            # manual update
            Tag.button(self.s_cpt, _onclick=self.do_click)
            
            # task update
            Tag.div( self.s_time )
        
    def on_mount(self):
        # at each mount (at 1st and following F5), this code is executed
        # to mount things
        async def run_next():
            while 1:
                self.s_time += 1
                await asyncio.sleep(0.5)
        self.task = asyncio.create_task(run_next())
        
    def on_unmount(self):
        # at each onmount (at end and following F5), this code is executed
        # to unmount things
        self.task.cancel()
    
    def do_click(self, o):
        self.s_cpt += 1


if __name__ == "__main__":
    ChromeApp(Tutu).run(reload=False)
