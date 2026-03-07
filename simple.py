from htag import Tag, ChromeApp, State, prevent, stop
import time

class Box(Tag.div):
    styles=".box {border:1px solid green;padding:8px}"
    def init(self):
        self._class = "box"

class Showcase(Tag.App):
    styles='''html,body {margin:0px;padding:0px}''' # scoped
    
    def init(self):
        self.s_cpt=State(0)
        self.s_liste=State(["A",]) #mutable
        self.s_dico=State({}) #mutable
        self.s_text=State("hello")
        

        with self:
            with Box():
                Tag.button("+1", _onclick=lambda ev: self.s_cpt.set(self.s_cpt.value + 1))
                Tag.div(self.s_cpt)

            with Box():
                Tag.button("+liste", _onclick=lambda ev: self.s_liste.append("b"))
                Tag.div(self.s_liste)

            with Box():
                Tag.button("+dict", _onclick=lambda ev: self.s_dico.update({time.time(): 42}))
                Tag.div(self.s_dico)

            with Box():

                # change on each key press
                Tag.input(_value=self.s_text.value, _onkeyup=lambda ev: self.s_text.set(ev.value))
                Tag.div(self.s_text)

                # change on blur
                Tag.input(_value=self.s_text, _onchange=lambda ev: self.s_text.set(ev.value))
                Tag.div(self.s_text)


if __name__ == "__main__":
    ChromeApp(Showcase).run(reload=True)
