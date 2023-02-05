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


def test_session():
    s=commons.Sessions()
    # assert in all case, it returns a dict {apps,session}
    x=s.get_ses("guid1")
    assert x["apps"]=={}        # its running apps
    assert x["session"]=={}     # its session dict

    # test base concept of session
    x["session"]["my_var"]="hello"

    x=s.get_ses("guid2")
    assert x["session"]=={}

    x=s.get_ses("guid1")
    assert "my_var" in x["session"]

def test_session_apps():
    s=commons.Sessions()

    s.set_hr( "fqn1|guid", "hr1")

    assert s.htuids == ["guid"]
    assert s.sesids == ["fqn1|guid"]

    s.set_hr( "fqn2|guid", "hr2")

    assert s.htuids == ["guid"]
    assert s.sesids == ["fqn1|guid","fqn2|guid"]

    assert s.del_hr( "fqn?|guid")==False
    assert s.del_hr( "fqn2|guid")==True

    assert s.htuids == ["guid"]
    assert s.sesids == ["fqn1|guid"]

if __name__=="__main__":
    test_default()
