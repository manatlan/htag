import sys
#######################################################
from app1 import App
#######################################################
import htag.runners
runner = getattr( htag.runners, sys.argv[1])
app=runner(App)
if runner in [htag.runners.AndroidApp,htag.runners.WebHTTP,]:
    app.run()
else:
    app.run( openBrowser=False )
