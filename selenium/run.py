##################################################################################################
## Run the runner 'sys.argv[1]' with the App 'sys.argv[2]'
## used by github action : .github/workflows/selenium.yaml
##################################################################################################

import sys,importlib
#######################################################
runner = sys.argv[1]
App=importlib.import_module(sys.argv[2]).App
port=int(sys.argv[3]) if len(sys.argv)>3 else 8000
#######################################################
import hclient
hclient.run( App, runner, openBrowser=False, port=port)
