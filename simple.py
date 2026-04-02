from htag import Tag, ChromeApp, States, prevent, stop
import time

class Box(Tag.div):
    styles=".box {border:1px solid green;padding:8px}"
    def init(self):
        self["class"] = "box"

class Showcase(Tag.App):
    styles='''html,body {margin:0px;padding:0px}''' # scoped
    
    def init(self):
        self.states=States(
            cpt=0,
            liste=["A",],
            dico={},
            text="hello"
        )
        

        with self:
            with Box():
                Tag.button("+1", _onclick=lambda ev: self.states.cpt.set(self.states.cpt.value + 1))
                Tag.div(self.states.cpt)

            with Box():
                Tag.button("+liste", _onclick=lambda ev: self.states.liste.append("b"))
                Tag.div(self.states.liste)

            with Box():
                Tag.button("+dict", _onclick=lambda ev: self.states.dico.update({time.time(): 42}))
                Tag.div(self.states.dico)

            with Box():

                # change on each key press
                Tag.input(_value=self.states.text.value, _onkeyup=lambda ev: self.states.text.set(ev.value))
                Tag.div(self.states.text)

                # change on blur
                Tag.input(_value=self.states.text, _onchange=lambda ev: self.states.text.set(ev.value))
                Tag.div(self.states.text)


if __name__ == "__main__":
    ChromeApp(Showcase).run(reload=True)
