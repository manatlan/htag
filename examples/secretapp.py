# -*- coding: utf-8 -*-
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

"""
Here is an example of an Htag App, runned in an own-made runner (see below)
which encrypt/decrypt exchanges between client/front and server/back,
for privacy needs !

the concept : encrypt/decrypt methods should exist in js and py sides
(doing the same kind of encryption/decyption ;-) )
(here, avoid to put the js password in clear in the js file !!!!!!)

But you could encrypt/decrypt communications with AES/GCM and a master pass
in both sides. To avoid MITM/proxy to capture exchanges ;-)
The concepts are the same.
"""

MASTERPASSWORD="password"

# #############################################################################
# the Htag app
# #############################################################################

from htag import Tag

class App(Tag.body):

    def init(self):
        self <= Tag.button("test",_onclick=self.print)

    def print(self,o):
        self += "hello"



# #############################################################################
# here is a specific runner (inspired from BrowserStarletteHTTP), which
# encrypt/decrypt exchanges between client/front/ui and server/back/python
# #############################################################################

from htag import Tag
from htag.render import HRenderer
from htag.runners import commons

import os

from starlette.applications import Starlette
from starlette.responses import HTMLResponse,PlainTextResponse
from starlette.routing import Route


# import base64,json
# def encrypt(str:str):
#     return base64.b64encode(str.encode()).decode()
# def decrypt(s:bytes):
#     return base64.b64decode(s).decode()

from Crypto.Cipher import AES
import hashlib
import base64,os,json
# https://hackernoon.com/how-to-use-aes-256-cipher-python-cryptography-examples-6tbh37cr

def decrypt(b64:bytes,key:str) -> bytes:   # text
    data=base64.b64decode(b64)
    key = hashlib.sha256(key.encode()).digest()
    cipher = AES.new(key, AES.MODE_GCM, data[:12]) # nonce
    return cipher.decrypt_and_verify(data[12:-16], data[-16:]) # ciphertext, tag

def encrypt(data:bytes,key:str) -> str:   # b64 cypĥertext
    key = hashlib.sha256(key.encode()).digest()
    iv = os.urandom(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    cyphertext,tag = cipher.encrypt_and_digest(data) # ciphertext, tag
    return base64.b64encode(iv + cyphertext + tag).decode()




class SecretApp(Starlette):
    """ Same as BrowserStarletteHTTP

        The instance is an ASGI htag app
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        self.hrenderer = None
        self.tagClass = tagClass

        Starlette.__init__(self,debug=True, routes=[
            Route('/', self.GET, methods=["GET"]),
            Route('/', self.POST, methods=["POST"]),
        ])

    def instanciate(self,url:str):
        init = commons.url2ak(url)
        if self.hrenderer and self.hrenderer.init == init:
            return self.hrenderer

        js = """

async function encrypt(plaintext, password) {
    const pwUtf8 = new TextEncoder().encode(password);                                 // encode password as UTF-8
    const pwHash = await crypto.subtle.digest('SHA-256', pwUtf8);                      // hash the password


    const iv = crypto.getRandomValues(new Uint8Array(12));                             // get 96-bit random iv
    const ivStr = Array.from(iv).map(b => String.fromCharCode(b)).join('');            // iv as utf-8 string

    const alg = { name: 'AES-GCM', iv: iv };                                           // specify algorithm to use

    const key = await crypto.subtle.importKey('raw', pwHash, alg, false, ['encrypt']); // generate key from pw

    const ptUint8 = new TextEncoder().encode(plaintext);                               // encode plaintext as UTF-8
    const ctBuffer = await crypto.subtle.encrypt(alg, key, ptUint8);                   // encrypt plaintext using key

    const ctArray = Array.from(new Uint8Array(ctBuffer));                              // ciphertext as byte array
    const ctStr = ctArray.map(byte => String.fromCharCode(byte)).join('');             // ciphertext as string

    return btoa(ivStr+ctStr);                                                          // iv+ciphertext base64-encoded
}


async function decrypt(ciphertext, password) {
    const pwUtf8 = new TextEncoder().encode(password);                                 // encode password as UTF-8
    const pwHash = await crypto.subtle.digest('SHA-256', pwUtf8);                      // hash the password

    const ivStr = atob(ciphertext).slice(0,12);                                        // decode base64 iv
    const iv = new Uint8Array(Array.from(ivStr).map(ch => ch.charCodeAt(0)));          // iv as Uint8Array

    const alg = { name: 'AES-GCM', iv: iv };                                           // specify algorithm to use

    const key = await crypto.subtle.importKey('raw', pwHash, alg, false, ['decrypt']); // generate key from pw

    const ctStr = atob(ciphertext).slice(12);                                          // decode base64 ciphertext
    const ctUint8 = new Uint8Array(Array.from(ctStr).map(ch => ch.charCodeAt(0)));     // ciphertext as Uint8Array
    // note: why doesn't ctUint8 = new TextEncoder().encode(ctStr) work?

    const plainBuffer = await crypto.subtle.decrypt(alg, key, ctUint8);            // decrypt ciphertext using key
    const plaintext = new TextDecoder().decode(plainBuffer);                       // plaintext from ArrayBuffer
    return plaintext;                                                              // return the plaintext
}


async function interact( o ) {
    let password="%s";   // <= DONT PUT THE PASSWORD HERE IN A JS FILE ! (use localStorage !)

    let encrypted = await encrypt(JSON.stringify(o),password);
    let req = await window.fetch("/",{method:"POST", body: encrypted});
    let payload = await req.text();
    let decrypted = await decrypt( payload ,password);
    action( decrypted );
}

window.addEventListener('DOMContentLoaded', start );
""" % MASTERPASSWORD

        return HRenderer(self.tagClass, js, lambda: os._exit(0), init=init)

    async def GET(self,request) -> HTMLResponse:
        self.hrenderer = self.instanciate( str(request.url) )
        return HTMLResponse( str(self.hrenderer) )

    async def POST(self,request) -> PlainTextResponse:
        data = json.loads( decrypt(await request.body(), MASTERPASSWORD) )
        dico = await self.hrenderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
        return PlainTextResponse( encrypt( json.dumps(dico).encode() ,MASTERPASSWORD) )

    def run(self, host="127.0.0.1", port=8000, openBrowser=True):   # localhost, by default !!
        import uvicorn,webbrowser
        if openBrowser:
            webbrowser.open_new_tab(f"http://{host}:{port}")

        uvicorn.run(self, host=host, port=port)



# #############################################################################
# the runner part
# #############################################################################
app=SecretApp( App )
if __name__ == "__main__":
    app.run()
