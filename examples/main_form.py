# -*- coding: utf-8 -*-
from htag import Tag, ChromeApp, State, prevent
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("form_app")

class FormApp(Tag.App):
    """
    A premium htag v2 example demonstrating unified form handling.
    It shows how to collect various input types into a single dictionary
    delivered by the form's 'submit' event.
    """
    
    # Global styles for typography and layout
    statics = [
        Tag.link(_rel="stylesheet", _href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap"),
        Tag.style("""
            body { 
                font-family: 'Outfit', sans-serif; 
                background: #f0f4f8; 
                color: #1a202c; 
                margin: 0; 
                padding: 40px 20px; 
                min-height: 100vh;
                display: flex;
                justify-content: center;
            }
            .container { 
                max-width: 800px; 
                width: 100%;
                animation: fadeIn 0.6s ease-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        """)
    ]

    # Scoped styles for the form component components
    styles = """
        .card { 
            background: white; 
            border-radius: 24px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.05); 
            padding: 40px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.8);
        }
        .header { margin-bottom: 40px; text-align: center; }
        .header h1 { 
            font-size: 2.5rem; 
            font-weight: 700; 
            margin: 0; 
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p { color: #718096; margin-top: 8px; font-size: 1.1rem; }

        .form-grid { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 24px; 
        }
        .full-width { grid-column: span 2; }
        
        .field { display: flex; flex-direction: column; gap: 8px; }
        .field label { font-weight: 600; color: #4a5568; font-size: 0.9rem; }
        
        .input-control { 
            padding: 12px 16px; 
            border: 2px solid #edf2f7; 
            border-radius: 12px; 
            font-size: 1rem; 
            font-family: inherit;
            transition: all 0.2s;
            outline: none;
        }
        .input-control:focus { border-color: #4f46e5; box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); }
        
        .radio-group, .checkbox-group { display: flex; gap: 20px; align-items: center; padding: 8px 0; }
        .radio-item, .checkbox-item { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        
        .btn-submit { 
            background: #4f46e5; 
            color: white; 
            border: none; 
            padding: 16px 32px; 
            border-radius: 12px; 
            font-weight: 700; 
            font-size: 1.1rem; 
            cursor: pointer; 
            transition: all 0.2s;
            margin-top: 20px;
            width: 100%;
            box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.3);
        }
        .btn-submit:hover { background: #4338ca; transform: translateY(-2px); box-shadow: 0 20px 25px -5px rgba(79, 70, 229, 0.4); }
        .btn-submit:active { transform: translateY(0); }

        .results { 
            background: #f8fafc; 
            border-radius: 16px; 
            padding: 24px; 
            border: 1px dashed #cbd5e0;
            animation: slideIn 0.4s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; scale: 0.95; }
            to { opacity: 1; scale: 1; }
        }
        .result-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #edf2f7; }
        .result-label { font-weight: 600; color: #718096; }
        .result-value { color: #1a202c; font-family: monospace; }
        .result-value.tag { 
            background: #e2e8f0; 
            padding: 2px 8px; 
            border-radius: 12px; 
            font-size: 0.8rem; 
            font-family: inherit; 
            font-weight: 500;
        }
    """

    def init(self):
        # State to hold the submitted form data
        self.form_data = State(None)

        with Tag.div(_class="container"):
            # Header section
            with Tag.div(_class="header"):
                Tag.h1("Universal Form Helper")
                Tag.p("Testing htag v2's unified form submission")

            # Main Form Card
            with Tag.div(_class="card"):
                with Tag.form(_onsubmit=self.handle_submit) as f:
                    with Tag.div(_class="form-grid"):
                        # Text Input
                        with Tag.div(_class="field"):
                            Tag.label("Full Name")
                            Tag.input(_name="fullname", _placeholder="John Doe", _class="input-control", _required=True)
                        
                        # Email Input
                        with Tag.div(_class="field"):
                            Tag.label("Email Address")
                            Tag.input(_type="email", _name="email", _placeholder="john@example.com", _class="input-control")

                        # Number Input
                        with Tag.div(_class="field"):
                            Tag.label("Age")
                            Tag.input(_type="number", _name="age", _value="25", _min="1", _max="120", _class="input-control")

                        # Date Input
                        with Tag.div(_class="field"):
                            Tag.label("Birth Date")
                            Tag.input(_type="date", _name="birthdate", _class="input-control")

                        # Select Dropdown
                        with Tag.div(_class="field"):
                            Tag.label("Country")
                            with Tag.select(_name="country", _class="input-control"):
                                Tag.option("France", _value="FR")
                                Tag.option("United Kingdom", _value="UK")
                                Tag.option("United States", _value="US")
                                Tag.option("Japan", _value="JP")

                        # Range Input
                        with Tag.div(_class="field"):
                            Tag.label("Skill Level")
                            Tag.input(_type="range", _name="level", _min="0", _max="100", _value="50", _class="input-control")

                        # Color Input
                        with Tag.div(_class="field"):
                            Tag.label("Brand Color")
                            Tag.input(_type="color", _name="theme_color", _value="#4f46e5", _class="input-control", _style="height: 50px; padding: 4px;")

                        # Time Input
                        with Tag.div(_class="field"):
                            Tag.label("Preferred Time")
                            Tag.input(_type="time", _name="time_pref", _class="input-control")

                        # Radio Group
                        with Tag.div(_class="field full-width"):
                            Tag.label("Gender")
                            with Tag.div(_class="radio-group"):
                                with Tag.label(_class="radio-item"):
                                    Tag.input(_type="radio", _name="gender", _value="male", _checked=True)
                                    Tag.span("Male")
                                with Tag.label(_class="radio-item"):
                                    Tag.input(_type="radio", _name="gender", _value="female")
                                    Tag.span("Female")
                                with Tag.label(_class="radio-item"):
                                    Tag.input(_type="radio", _name="gender", _value="other")
                                    Tag.span("Other")

                        # Textarea
                        with Tag.div(_class="field full-width"):
                            Tag.label("Short Bio")
                            Tag.textarea(_name="bio", _placeholder="Tell us about yourself...", _class="input-control", _style="height: 100px;")

                        # Checkbox
                        with Tag.div(_class="field full-width"):
                            with Tag.label(_class="checkbox-item"):
                                Tag.input(_type="checkbox", _name="subscribe", _checked=True)
                                Tag.span("Subscribe to newsletter")

                    Tag.button("Submit Profile", _type="submit", _class="btn-submit")

            # Results section (Reactive)
            Tag.div(lambda: self.render_results(), _class="container")

    def render_results(self):
        """Renders the data received from the form."""
        if not self.form_data.value:
            return None
        
        with Tag.div(_class="card") as root:
            Tag.h2("Submission Result", _style="margin-top:0; color:#4f46e5;")
            Tag.p("The following dictionary was received in e.value:", _style="color:#718096; margin-bottom: 20px;")
            
            with Tag.div(_class="results"):
                for key, val in self.form_data.value.items():
                    with Tag.div(_class="result-item"):
                        Tag.span(key, _class="result-label")
                        # Handle checkbox/boolean display
                        if isinstance(val, bool) or val in ("on", "off"):
                            Tag.span(str(val), _class="result-value tag")
                        else:
                            Tag.span(str(val) if val else "(empty)", _class="result-value")
            
            Tag.button("Clear Results", _onclick=lambda e: self.form_data.set(None), 
                       _class="btn-submit", _style="margin-top:24px; background: #94a3b8;")
        return root

    @prevent
    def handle_submit(self, e):
        """
        Unified handler for the form submission.
        'e.value' contains all form fields keyed by their '_name'.
        """
        logger.info("Form received: %s", e.value)
        self.form_data.value = e.value
        # Scroll to result or show a success message could be added here
        self.call_js("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'})")

if __name__ == "__main__":
    # In V2, we just run the App class
    ChromeApp(FormApp, width=900, height=1000).run(reload=True)
