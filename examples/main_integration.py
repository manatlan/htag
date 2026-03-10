# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "htag",
#     "itsdangerous",
#     "python-multipart",
# ]
# [tool.uv.sources]
# htag = { path = ".." }
# ///

from htag import Tag, WebApp
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
import uvicorn

# --- 1. Create htag app ---
class MyApp(Tag.App):
    def init(self):
        # The request is now automatically available in all tags!
        # (It's updated on every interaction)
        username = self.request.session.get("username", "Anonyme")

        self["style"] = "font-family: sans-serif; padding: 20px; border: 2px solid #646cff; border-radius: 8px; max-width: 400px; margin: 20px auto; text-align: center;"
        self <= Tag.h2(f"Welcome to htag, {username}!")
        self <= Tag.p("I am mounted at /app")
        
        def change_name(e):
            # Mutate Starlette session directly!
            self.request.session["username"] = "Admin_Htag"
            # In htag, we just update the UI
            self.clear()
            self.init()

        self <= Tag.button("Change name to Admin_Htag", _onclick=change_name)
        self <= Tag.div(Tag.a("Back to HTML home", _href="/"), _style="margin-top:20px")


# --- 2. Main Starlette application creation ---
app = Starlette(
    middleware=[
        Middleware(SessionMiddleware, secret_key="super-secret-key"),
    ]
)

@app.route("/")
async def home(request):
    # Set a default name if empty
    if "username" not in request.session:
        request.session["username"] = "Visiteur"
        
    username = request.session.get("username")
    
    return HTMLResponse(f"""
        <html>
            <body style="font-family: sans-serif; padding: 50px; text-align:center;">
                <h1>Starlette Home</h1>
                <p>Hello <b>{username}</b>! This is a standard Starlette route.</p>
                <form method="POST" action="/login">
                    <input type="text" name="user" placeholder="Enter your name">
                    <button type="submit">Set Session</button>
                </form>
                <hr>
                <a href="/app" style="font-size: 1.5em; color: #646cff;">Launch htag App (/app)</a>
            </body>
        </html>
    """)

@app.route("/login", methods=["POST"])
async def login(request):
    form = await request.form()
    if form.get("user"):
        request.session["username"] = form["user"]
    return RedirectResponse(url="/", status_code=303)


# --- 3. Mount htag app ---
app.mount("/app", WebApp(MyApp).app) 

if __name__ == "__main__":
    import os
    import sys

    # Enable htag auto-reload polling in the frontend
    MyApp._reload = True
    
    print("🚀 Server started at http://127.0.0.1:8000 (with hot-reload)")
    
    # We use the string import path to allow uvicorn's reload feature
    file_name = os.path.basename(__file__)[:-3] # "main_integration"
    uvicorn.run(f"{file_name}:app", host="127.0.0.1", port=8000, reload=True)
