# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

import os,sys

devappmode=False

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

if __name__=="__main__":
    if len(sys.argv)>1:
        ##########################################################################
        ## run mode
        ##########################################################################
        htagfile=os.path.realpath(sys.argv[1])

        try:
            from htag.runners import Runner
            import importlib.util
            module_name=os.path.basename(htagfile)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, htagfile)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            if hasattr(module,"app"):
                app=getattr(module,"app")
                if isinstance(app,Runner):
                    print("Found 'app' (new Runner), will run it")
                    print(app,"Serving")
                    # run part (like defined in file)
                    app.run()
                    sys.exit(0)

            if hasattr(module,"App"):
                print("Found 'App' (tag class), will run it")
                tagClass=getattr(module,"App")

                # run part (here FULL DEV, and open a tab/browser)
                app=Runner(tagClass,reload=True,debug=True)
                print(app,"Serving")
                app.run()
            else:
                print("ERROR",htagfile,"doesn't contain 'App' (tag class)")
        except Exception as e:
            print("ERROR",e)
    else:
        ##########################################################################
        ## create mode
        ##########################################################################
        newfile = "main.py"

        if not os.path.isfile(newfile):
            with open(newfile,"w+") as fid:
                fid.write(code)

            print("HTag App file created --> main.py")
        else:
            print(f"It seems that you've already got a {newfile} file")
