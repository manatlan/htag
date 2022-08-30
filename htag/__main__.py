# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

import os,stat

try:
    import pip

    # install uvicorn if not present (for DevApp mode)
    try:
        import uvicorn
    except ImportError as e:
        pip.main(['install', 'uvicorn[standard]'])

    # install starlette if not present (for DevApp mode)
    try:
        import starlette
    except ImportError as e:
        pip.main(['install', 'starlette'])

    devappmode = True
except:
    devappmode = False


code = """
# -*- coding: utf-8 -*-
# the simplest htag'app, in the best env to start development (hot reload/refresh)

from htag import Tag

class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self += "Hello World"

#=================================================================================
%s
# from htag.runners import BrowserHTTP as Runner
# from htag.runners import ChromeApp as Runner

app=Runner(App)
if __name__=="__main__":
    app.run()
""" % (devappmode and "from htag.runners import DevApp as Runner" or "from htag.runners import BrowserHTTP as Runner")

newfile = "main.py"

if not os.path.isfile(newfile):
    with open(newfile,"w+") as fid:
        fid.write(code)

    print("HTag App file created --> main.py")
else:
    print(f"It seems that you've already got a {newfile} file")
