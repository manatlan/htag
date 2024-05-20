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
        self <= "Hello World"
        self <= Tag.button("Say hi", _onclick=self.sayhi)

    def sayhi(self,ev):
        self <= "hi!"


#=================================================================================
from htag.runners import Runner

if __name__ == "__main__":
    Runner(App).run()
"""

import argparse

class BooleanOptionalAction(argparse.Action):
    """ only here for compatibility with py < 3.9 """
    def __init__(self, option_strings, dest, default=None, required=False, help=None, **kwargs):
        # Créer les options avec et sans 'no'
        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)
            if option_string.startswith('--'):
                _option_strings.append(option_string.replace('--', '--no-'))
        
        super(BooleanOptionalAction, self).__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            const=None,
            default=default,
            required=required,
            help=help,
            **kwargs
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string.startswith('--no-'):
            setattr(namespace, self.dest, False)
        else:
            setattr(namespace, self.dest, True)
    
    def format_help(self):
        return f"{', '.join(self.option_strings)}: {self.help} (default: {self.default})"

if __name__=="__main__":

    parser = argparse.ArgumentParser(
        prog="htag",
        description="""Entrypoint to help you <to create> or <to run> a htag'app.
If a [file] is given: it will try to run it (using dev mode),
else it will create an empty htag file named 'main.py' in current path. Options are just here for the run mode.
""",
    )
    parser.add_argument('file', nargs='?', help="if present, the htag'file will be runned (in dev mode)")
    parser.add_argument('--host', help='Host listener [default: 127.0.0.1]', default="127.0.0.1")
    parser.add_argument('--port', help='Port number [default: 8000]', default="8000")
    parser.add_argument('--gui', help="Automatically open interface in a browser [default]",action=BooleanOptionalAction, default=True)
    parser.add_argument('--dev', help="Run in dev mode (reload+debug) [default]",action=BooleanOptionalAction, default=True)
    args = parser.parse_args()
    if args.file:
        ##########################################################################
        ## run mode
        ##########################################################################
        htagfile=os.path.realpath(args.file)
        try:
            assert os.path.isfile(htagfile), f"file '{htagfile}' not found"
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
                app=Runner(tagClass,reload=args.dev,debug=args.dev,host=args.host,port=args.port, interface=1 if args.gui else 0)
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
