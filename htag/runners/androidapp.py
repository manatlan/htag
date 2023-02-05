# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################


from htag import Tag
from htag.render import HRenderer
from . import commons

import os,json,asyncio

import tornado.ioloop
import tornado.web
import tornado.platform.asyncio

from threading import Thread

class WebServer(Thread): # the webserver is ran on a separated thread

    def __init__(self,instance,port):
        super(WebServer, self).__init__()
        self.instance=instance
        self.port=port

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        tornado.platform.asyncio.AsyncIOMainLoop().install()

        class MainHandler(tornado.web.RequestHandler):
            async def get(this):
                self.instance.instanciate( str(this.request.uri)  )
                this.write( str(self.instance.renderer) )
            async def post(this):
                data = json.loads( this.request.body.decode() )
                dico = await self.instance.renderer.interact(data["id"],data["method"],data["args"],data["kargs"],data.get("event"))
                this.write(json.dumps(dico))

        app = tornado.web.Application([(r"/", MainHandler),])
        app.listen(self.port)

        self.loop=asyncio.get_event_loop()
        self.loop.run_forever()


class AndroidApp:
    """
    An "Android Runner", for an HTag App. Which will only work on android/platform

    BTW : it uses tornado/http
    """
    def __init__(self,tagClass:type):
        assert issubclass(tagClass,Tag)

        self.renderer=None
        self.tagClass=tagClass

    def instanciate(self,url:str):
        init = commons.url2ak(url)
        if self.renderer and self.renderer.init == init:
            return self.renderer

        js = """
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).text() )
}

window.addEventListener('DOMContentLoaded', start );
"""
        self._exiter=None
        hr=HRenderer(self.tagClass, js, self.go_exit, init=init)
        self.renderer=hr
        return hr

    def go_exit(self):
        if self._exiter is None:
            os._exit(0)
        else:
            self._exiter()

    def run(self): # basically, the same code as guy.runAndroid()
        host,port= "127.0.0.1", 12458
        urlStartPage = f"http://{host}:{port}"

        self.server = WebServer(self,port)

        #=================================================================
        import kivy
        from kivy.app import App
        from kivy.utils import platform
        from kivy.uix.widget import Widget
        from kivy.clock import Clock
        from kivy.logger import Logger

        def run_on_ui_thread(arg):
            pass

        webView       = None
        webViewClient = None
        activity      = None
        if platform == 'android':
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            webView       = autoclass('android.webkit.WebView')
            webViewClient = autoclass('android.webkit.WebViewClient')
            activity      = autoclass('org.kivy.android.PythonActivity').mActivity
        else:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("SHOULD BE RUN ON ANDROID (you are on '%s') fallback to browser !!!" % platform)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            import webbrowser
            webbrowser.open_new_tab(urlStartPage)
            self.server.start()
            return

        # better: https://karobben.github.io/2021/04/30/Python/kivy_android_webviewer/ ?

        class Wv(Widget):
            def __init__(self, runner ):
                self.f2 = self.create_webview               # ! important
                super(Wv, self).__init__()
                self.visible = False

                def exit_app(*a,**k):
                    activity.finish()
                    App.get_running_app().stop()
                    os._exit(0)

                runner._exiter=exit_app

                runner.server.start()                       # ! important

                Clock.schedule_once(self.create_webview, 0)

            @run_on_ui_thread
            def create_webview(self, *args):
                webview = webView(activity)
                webview.getSettings().setJavaScriptEnabled(True)
                webview.getSettings().setDomStorageEnabled(True)
                webview.setWebViewClient(webViewClient())
                activity.setContentView(webview)
                webview.loadUrl(urlStartPage)               # !important

        class ServiceApp(App):
            def build(this):
                return Wv( self )

        ServiceApp().run()
        #=================================================================

