from imp import reload
import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag

"""
AUTORELOAD is possible with this two runners : WebHTTP & BrowserStarletteHTTP
(could be very handy in development phase)

See this example, on how to instanciate the runner and use uvicorn/autoreload
"""

class Demo(Tag.div):
    statics=[ Tag.style("""body {background:#EEE}""") ]

    def init(self):
        for c in range(2000000,16581375,10000):
            self <= Tag.button("Hello",_style=f"background:#{hex(c)[2:]}")

#############################################################################################

from htag.runners import *

app = BrowserStarletteHTTP( Demo )
# app = WebHTTP( Demo )

if __name__=="__main__":
    import uvicorn
    uvicorn.run("autoreload:app",host="127.0.0.1",port=8000,reload=True,factory=True)