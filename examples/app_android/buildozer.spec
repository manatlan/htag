[app]
title = Main
package.name = main
package.domain = org.htag
version = 1.0

source.dir = .
source.include_exts = py,png,jpg,jpeg,svg,js,css,html

requirements = android,htag,starlette,uvicorn,websockets,anyio,typing_extensions,click,httpx,h11
orientation = portrait
fullscreen = 0
android.archs = arm64-v8a
android.api = 35
android.minapi = 24
android.ndk = 28
icon.filename = %(source.dir)s/icon.png

home_app = 1
android.permissions = INTERNET
android.accept_sdk_license = True

p4a.hook = p4a/hook.py
p4a.port = 13333
p4a.bootstrap = webview
p4a.branch = v2024.01.21
[buildozer]
log_level = 2
