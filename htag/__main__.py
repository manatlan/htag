# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

import os,sys

code = """
# -*- coding: utf-8 -*-

from htag import Tag

class App(Tag.body):
    statics="body {background:#EEE;}"

    def init(self):
        self += "Hello World"
        self += Tag.button("Say hi", _onclick=self.sayhi)

    def sayhi(self,o):
        self+="hi!"

#=================================================================================
from htag.runners import Runner

if __name__ == "__main__":
    Runner(App).run()
"""

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

            print("HTag App file created -->", newfile)
        else:
            print(f"It seems that you've already got a '{newfile}' file")
