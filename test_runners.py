import pytest,time
import importlib
from htag import Tag

class MyApp(Tag.div):
    def init(self):
        self <= "Hello World"


def test_default():
    from htag.runners import Runner
    app=Runner( MyApp )
    #TODO: test app.add_route( )
    #TODO: test app.handle( )

def data_source():
    for i in  [
        "DevApp",
        "BrowserStarletteHTTP",
        "BrowserStarletteWS",
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


def test_route_match():
    assert commons.match( "/{val}","/jo" ) == {"val":"jo"}
    assert commons.match( "/{val:str}","/jo" ) == {"val":"jo"}
    assert commons.match( "/{v1}","/jo" ) == {"v1":"jo"}

    assert commons.match( "/item/{idx}","/item/1" ) == {"idx":"1"}
    assert commons.match( "/item/{idx:int}","/item/1" ) == {"idx":1}

    assert commons.match( "/download/{rest_of_path:path}","/download/pub/image.png" ) == {"rest_of_path":"pub/image.png"}


    assert not commons.match( "/xxx","/ppp" )
    assert not commons.match( "/item/{idx}","/" )
    assert not commons.match( "/item/{idx}","/item" )
    assert not commons.match( "/item/{idx}","/item/" )

if __name__=="__main__":
    test_default()
