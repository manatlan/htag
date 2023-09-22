import sys
from htag import Tag # the only thing you'll need ;-)

class Percent(Tag.div):
    def init(self,v):
        self.value=v
        self["style"]="width:100px;height:20px;border:1px solid black"
    def render(self):
        self <= Tag.div(_style="height:20px;background:blue;width:%s%%;" % self.value)


class Gui4(Tag.body):
    """ https://eugenkiss.github.io/7guis/tasks/#timer """
    """ https://svelte.dev/examples/7guis-timer """

    #TODO: finnish it
    #TODO: finnish it
    #TODO: finnish it
    #TODO: finnish it
    #TODO: finnish it

    def init(self):
        self.value=10
        self.gauge = Percent(20)

    def render(self):
        self.clear()
        self <= self.gauge

        self <= Tag.input(
            _value=self.value,
            _type="range",
            _min=1,
            _max=100,
            _step=1,
            _onchange=self.bind.change(b"this.value")
        )
        self<=Tag.button("Reset")

    def change(self,v):
        self.value=v

        self.gauge.value=v  # FOR TEST ONLY


App=Gui4
if __name__=="__main__":
    # and execute it in a pywebview instance
    from htag.runners import *
    PyWebWiew( Gui4 ).run()

    # here is another runner, in a simple browser (thru ajax calls)
    # BrowserHTTP( Page ).run()
