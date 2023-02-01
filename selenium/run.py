import sys
#######################################################
runner = sys.argv[1]
import importlib
App=importlib.import_module(sys.argv[2]).App
#######################################################
import htag.runners
runner = getattr( htag.runners, runner)
app=runner(App)
if runner in [htag.runners.AndroidApp,htag.runners.WebHTTP,]:
    app.run()
else:
    app.run( openBrowser=False )
