import pytest,time
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
        #"PyWebWiew",    # before 0.8.0 (mispelling)
        "PyWebView",
        #"ChromeApp", # need Chrome installed ;-(
        #"WinApp", # need Chrome installed ;-(
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
        assert hasattr(r,"run")
    else:
        print("can't test %s" % my_runner)


from htag.runners import commons


def test_url2ak():
    assert commons.url2ak("") == ( (),{} )
    assert commons.url2ak("http://jojo.com/") == ( (),{} )
    assert commons.url2ak("http://jojo.com/?") == ( (),{} )
    assert commons.url2ak("http://jojo.com/???") == ( ("??",),{} )

    assert commons.url2ak("http://jojo.com/?kiki") == ( ("kiki",),{} )
    assert commons.url2ak("http://jojo.com/?kiki&koko") == ( ("kiki","koko"),{} )
    assert commons.url2ak("http://jojo.com/?kiki&&&") == ( ("kiki",),{} )
    assert commons.url2ak("http://jojo.com/?kiki???") == ( ("kiki???",),{} )

    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b=5") == (('1 2', 'kiki'), {'a': '3', 'b': '5'})

    # test a karg not valued
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b=") == (('1 2', 'kiki'), {'a': '3', 'b': None})

    # test an arg after kargs
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b") == (('1 2', 'kiki', 'b'), {'a': '3'})

    # test double kargs, the latest is the one
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b=5&b=6") == (('1 2', 'kiki'), {'a': '3', 'b': '6'})

    # test same ^^ url with anchor
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b=5&b=6#yolo") == (('1 2', 'kiki'), {'a': '3', 'b': '6'})


def test_webhttp_session_hr():
    s=commons.HRSessions()
    assert len(s._data)==0

    fqn1="fqn1"

    s.set_hr( fqn1, "hr1" )
    assert s.get_hr(fqn1) == "hr1"
    assert s.del_hr( fqn1)
    assert not s.del_hr( fqn1)
    assert s.get_hr(fqn1) == None

    assert len(s._data)==0

    s.set_hr( fqn1, "hr1" )
    assert s.purge(1)==0
    time.sleep(2)
    assert s.purge(1)==1
    assert len(s._data)==0


if __name__=="__main__":
    #test_default()
    test_webhttp_session_hr()