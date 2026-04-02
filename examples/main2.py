from htag import Tag, States
import logging

class MessageBox(Tag.div):
    styles = """ 
        .msgbox-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
        .msgbox-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.3); width: 450px; text-align: center; border-top: 6px solid #1a73e8; }
        .msgbox-title { margin-top: 0; color: #1a73e8; font-size: 1.8rem; margin-bottom: 15px; }
        .msgbox-text { margin-bottom: 30px; color: #4a5568; font-size: 1.1rem; line-height: 1.6; }
    """ # SCOPED !!!!!!!!!!!!!!!!!!!!
    
    def init(self, title, message):
        self._class="msgbox-overlay"
        with Tag.div(_class="msgbox-card"):
            Tag.h2(title, _class="msgbox-title")
            Tag.p(message, _class="msgbox-text")
            Tag.button("OK", _onclick=lambda e: self.remove(), _class="btn btn-primary btn-wide")

class MyApp(Tag.App):
    statics = [
        Tag.link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap"),
        Tag.style("""
            body { font-family: 'Inter', sans-serif; background: #f4f7f9; color: #333; margin: 0; padding: 40px; min-height: 100vh; }
            .container { max-width: 900px; margin: 0 auto; }
            h1 { color: #2c3e50; font-weight: 300; margin-bottom: 40px; font-size: 2.5rem; text-align: center; }
            
            .card { background: white; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; }
            .form-card { padding: 30px; margin-bottom: 40px; display: flex; align-items: center; gap: 20px; }
            
            .form-input { flex: 1; padding: 14px 20px; border: 2px solid #edf2f7; border-radius: 10px; outline: none; transition: border-color 0.2s; font-size: 1rem; }
            .form-input:focus { border-color: #1a73e8; }
            
            .btn { padding: 14px 28px; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 1rem; transition: transform 0.1s, background 0.2s; display: inline-block; }
            .btn:active { transform: scale(0.98); }
            .btn-primary { background: #1a73e8; color: white; box-shadow: 0 4px 12px rgba(26, 115, 232, 0.2); }
            .btn-primary:hover { background: #1557b0; }
            .btn-danger-light { padding: 4px 12px; background: #fee2e2; color: #ef4444; font-size: 1.2rem; border-radius: 8px; }
            .btn-danger-light:hover { background: #fecaca; }
            .btn-wide { padding-left: 60px; padding-right: 60px; }
            
            table { width: 100%; border-collapse: collapse; }
            th { background: #f8fafc; border-bottom: 2px solid #edf2f7; text-align: left; padding: 20px 25px; color: #718096; font-size: 0.75rem; letter-spacing: 0.1em; }
            td { padding: 20px 25px; border-bottom: 1px solid #edf2f7; color: #4a5568; }
            tr:last-child td { border-bottom: none; }
            tr:hover td { background-color: #fcfdfe; }
            .name-cell { font-weight: 500; color: #2d3748; }
        """)
    ]

    def init(self):
        # 1. État Réactif
        self.state = States(users=[
            {"name": "Alice Cooper", "age": 75},
            {"name": "Bob Marley", "age": 36}
        ])
        
        # 2. Construction déclarative (zero-boilerplate)
        with Tag.div(_class="container"):
            Tag.h1("User Directory")
            
            # Form Card
            with Tag.div(_class="card form-card"):
                self.i_name = Tag.input(_value="", _placeholder="Full Name", _class="form-input")
                self.i_age = Tag.input(_value="", _placeholder="Age", _type="number", _class="form-input", _style="flex: 0.3;")
                Tag.button("Add Member", _onclick=self.add_person, _class="btn btn-primary")
            
            # Table Container (Reactive via lambda)
            with Tag.div(_class="card"):
                with Tag.table():
                    with Tag.thead():
                        with Tag.tr():
                            Tag.th("NAME")
                            Tag.th("AGE")
                            Tag.th("")
                    
                    # 3. Rendu réactif des lignes
                    # Se rafraîchit à chaque fois que self.state.users.value change !
                    Tag.tbody(lambda: [
                        Tag.tr([
                            Tag.td(person["name"], _class="name-cell"),
                            Tag.td(str(person["age"])),
                            Tag.td(
                                Tag.button("×", 
                                    _onclick=lambda e, p=person: self.del_person(p), 
                                    _title="Remove member", 
                                    _class="btn btn-danger-light"
                                ), 
                                _style="text-align: right;"
                            )
                        ]) for person in self.state.users.value
                    ])

    def del_person(self, person):
        # On modifie la donnée "pûrement"
        new_list = [p for p in self.state.users.value if p != person]
        self.state.users.value = new_list
        logger.info("Deleted person: %s", person["name"])

    def add_person(self, event):
        name = self.i_name["value"]
        age = self.i_age["value"]
        if name and age:
            # On ajoute à la liste et on réassigne pour trigger la réactivité
            self.state.users.value = self.state.users.value + [{"name": name, "age": int(age)}]
            self.i_name["value"] = ""
            self.i_age["value"] = ""
            logger.info("Added person: %s", name)
        else:
            self <= MessageBox("Validation Error", "Please provide both a name and an age to continue.")

if __name__ == "__main__":
    from htag import ChromeApp
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("app")
    
    ChromeApp(MyApp, width=1024, height=768).run()
