##################################################################################################
## Run the runner 'sys.argv[1]' with the App 'sys.argv[2]'
## used by github action : .github/workflows/selenium.yaml
##################################################################################################

import sys,importlib
#######################################################
runner = sys.argv[1]
App=importlib.import_module(sys.argv[2]).App
#######################################################
import htag.runners

runner = getattr( htag.runners, runner)
app=runner(App)
if runner in [htag.runners.AndroidApp,htag.runners.WebHTTP,]:
    app.run()
else:
    app.run( openBrowser=False )
