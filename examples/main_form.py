# -*- coding: utf-8 -*-
from htag import Tag, ChromeApp, prevent

class FormApp(Tag.App):
    """
    A comprehensive and premium htag v2 example demonstrating the unified 
    form handling for ALL standard HTML input types.
    """
    
    statics = [
        Tag.link(_rel="stylesheet", _href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap"),
    ]

    styles = """
        body { 
            font-family: 'Outfit', sans-serif; 
            background: #f8fafc; 
            padding: 40px 20px; 
            display: flex; 
            justify-content: center; 
        }
        .container { max-width: 600px; width: 100%; }
        .card { 
            background: white; 
            padding: 30px; 
            border-radius: 20px; 
            box-shadow: 0 10px 25px rgba(0,0,0,0.05); 
            margin-bottom: 20px; 
        }
        h2 { margin: 0 0 20px; color: #1e293b; font-size: 1.5rem; }
        
        .field { margin-bottom: 15px; display: flex; flex-direction: column; gap: 5px; }
        label { font-size: 0.9rem; font-weight: 600; color: #64748b; }
        
        input[type="text"], input[type="email"], input[type="number"], 
        input[type="date"], input[type="time"], select, textarea {
            padding: 10px 12px;
            border: 2px solid #e2e8f0;
            border-radius: 10px;
            font-family: inherit;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus, select:focus, textarea:focus { border-color: #3b82f6; }
        
        .row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        
        .inline { display: flex; align-items: center; gap: 10px; font-weight: 400; color: #1e293b; }
        
        button {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 10px;
            font-weight: 700;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
            transition: background 0.2s;
        }
        button:hover { background: #2563eb; }
        
        .result-box { 
            background: #f1f5f9; 
            padding: 15px; 
            border-radius: 10px; 
            font-family: monospace; 
            white-space: pre-wrap; 
            font-size: 0.9rem;
            border: 1px solid #e2e8f0;
        }
    """

    def init(self):
        self.display = Tag.div("Press submit to see results...", _class="result-box")

        with Tag.div(_class="container"):
            with Tag.div(_class="card"):
                Tag.h2("Registration Form")
                with Tag.form(_onsubmit=self.handle_submit):
                    # Text & Email
                    with Tag.div(_class="row"):
                        with Tag.div(_class="field"):
                            Tag.label("Full Name")
                            Tag.input(_type="text", _name="name", _value="John Doe", _required=True)
                        with Tag.div(_class="field"):
                            Tag.label("Email")
                            Tag.input(_type="email", _name="email", _value="john@example.com")

                    # Number & Select
                    with Tag.div(_class="row"):
                        with Tag.div(_class="field"):
                            Tag.label("Age")
                            Tag.input(_type="number", _name="age", _value="30")
                        with Tag.div(_class="field"):
                            Tag.label("Role")
                            with Tag.select(_name="role"):
                                Tag.option("Developer", _value="dev")
                                Tag.option("Designer", _value="design")
                                Tag.option("Manager", _value="mgr")

                    # Date & Time
                    with Tag.div(_class="row"):
                        with Tag.div(_class="field"):
                            Tag.label("Birthday")
                            Tag.input(_type="date", _name="bday")
                        with Tag.div(_class="field"):
                            Tag.label("Meeting Time")
                            Tag.input(_type="time", _name="time")

                    # Range & Color
                    with Tag.div(_class="row"):
                        with Tag.div(_class="field"):
                            Tag.label("Experience (0-10)")
                            Tag.input(_type="range", _name="exp", _min="0", _max="10", _value="5")
                        with Tag.div(_class="field"):
                            Tag.label("Favorite Color")
                            Tag.input(_type="color", _name="color", _value="#3b82f6", _style="height:44px; padding:2px")

                    # Radio Buttons
                    with Tag.div(_class="field"):
                        Tag.label("Gender")
                        with Tag.div(_class="row"):
                            with Tag.label(_class="inline"):
                                Tag.input(_type="radio", _name="gender", _value="M", _checked=True)
                                Tag.span("Male")
                            with Tag.label(_class="inline"):
                                Tag.input(_type="radio", _name="gender", _value="F")
                                Tag.span("Female")

                    # Textarea
                    with Tag.div(_class="field"):
                        Tag.label("Short Bio")
                        Tag.textarea(_name="bio", _placeholder="Tell us a bit about yourself...")

                    # Checkbox
                    with Tag.label(_class="inline", _style="margin: 10px 0"):
                        Tag.input(_type="checkbox", _name="terms", _checked=True)
                        Tag.span("I agree to the terms and conditions")

                    Tag.button("Submit Profile", _type="submit")


    @prevent
    def handle_submit(self, e):
        # e.value is the dictionary of all fields
        # Note: checkboxes are "on" if checked, missing otherwise in standard HTML,
        # but htag ensures they are correctly captured.
        
        import json
        pretty_json = json.dumps(e.value, indent=4)
        
        # Simple display update without State
        self.display.clear()
        self.display.add(pretty_json)
        
if __name__ == "__main__":
    ChromeApp(FormApp).run()
