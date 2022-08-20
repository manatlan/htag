import pytest
import importlib
from htag import Tag

class MyApp(Tag.div):
    def init(self):
        self <= "Hello World"


def test_default():
    from htag.runners import BrowserHTTP
    BrowserHTTP( MyApp )

def data_source():
    for i in  [
        "DevApp",
        "BrowserStarletteHTTP",
        "BrowserStarletteWS",
        "WebHTTP",
        "PyWebWiew",
        "ChromeApp",
        "AndroidApp",
        "BrowserTornadoHTTP",
        "PyScript",
    ]:
        yield i

@pytest.mark.parametrize('my_runner', data_source())
def test_a_runner( my_runner ):
    mrunners=importlib.import_module("htag.runners")

    if hasattr(mrunners,my_runner):
        runner=getattr(mrunners,my_runner)
        r=runner( MyApp )
        # assert hasattr(r,"run")
    else:
        print("can't test %s" % my_runner)

if __name__=="__main__":
    test_default()
