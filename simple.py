from htag import Tag, ChromeApp, State, prevent, stop
import time

class Showcase(Tag.App):
    styles='html,body {margin:0px;padding:0px}' # scoped
    
    def init(self):
        self.cpt=State(0)
        self.liste=State(["A",]) #mutable
        self.dico=State({}) #mutable
        
        with self:
            Tag.button("+1",_onclick=self.on_click_cpt)
            Tag.div(self.cpt)

            Tag.button("+liste",_onclick=self.on_click_liste)
            Tag.div(self.liste)

            Tag.button("+dict",_onclick=self.on_click_dict)
            Tag.div(self.dico)

    def on_click_cpt(self,ev):
        self.cpt += 1
    def on_click_liste(self,ev):
        self.liste.append("b")
    def on_click_dict(self,ev):
        self.dico.update({time.time():42})

if __name__ == "__main__":
    ChromeApp(Showcase).run(reload=True)
