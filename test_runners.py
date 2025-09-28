import pytest,time
import importlib
from htag import Tag
from unittest.mock import Mock, patch, AsyncMock
import os
import asyncio
import json

class MyApp(Tag.div):
    def init(self):
        self <= "Hello World"


def test_default():
    from htag.runners import Runner
    app=Runner( MyApp )
    #TODO: test app.add_route( )
    #TODO: test app.handle( )

def test_runner_instantiation_and_methods_jules():
    from htag.runners import Runner

    app = Runner(MyApp)
    assert app.session is None
    assert app.host == "127.0.0.1"
    assert app.port == 8000
    assert not app.debug
    assert not app.reload
    assert not app.http_only
    assert app.interface == 1
    assert not app.use_first_free_port
    assert len(app._routes) == 1

    def handler(request):
        return "test"
    app.add_route("/test", handler)
    assert len(app._routes) == 2
    assert app._routes[1] == ("/test", handler)

    request = Mock()
    request.path = "/"
    app.server = Mock()
    app.handle(request, MyApp)
    app.server.doGet.assert_called_once()

    assert "127.0.0.1:8000" in str(app)

    with patch('os._exit') as mock_exit:
        app.chromeapp = None
        app.stop()
        mock_exit.assert_called_once_with(0)

def data_source():
    for i in  [
        "DevApp",
        "BrowserStarletteHTTP",
        "BrowserStarletteWS",
        "PyWebView",
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
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b=") == (('1 2', 'kiki'), {'a': '3', 'b': None})
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b") == (('1 2', 'kiki', 'b'), {'a': '3'})
    assert commons.url2ak("http://jojo.com/?1%202&kiki&a=3&b=5&b=6") == (('1 2', 'kiki'), {'a': '3', 'b': '6'})
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

def test_utility_functions_jules():
    from htag.runners.runner import isFree, reload, runChromeApp

    with patch('socket.socket') as mock_socket:
        mock_socket.return_value.connect_ex.return_value = 1
        assert isFree('localhost', 8080)
        mock_socket.return_value.connect_ex.return_value = 0
        assert not isFree('localhost', 8080)

    with patch('importlib.reload') as mock_reload:
        with patch('inspect.getmodule') as mock_getmodule:
            mock_module = Mock()
            setattr(mock_module, MyApp.__name__, MyApp)
            mock_getmodule.return_value = mock_module
            mock_reload.return_value = mock_module

            reloaded_class = reload(MyApp)
            mock_reload.assert_called_once_with(mock_module)
            assert reloaded_class == MyApp

    with patch('htag.runners.runner.ChromeApp') as mock_chrome_app:
        runChromeApp('localhost', 8000, (800, 600))
        mock_chrome_app.assert_called_once_with("http://localhost:8000", size=(800, 600))

    with patch('htag.runners.runner.ChromeApp', side_effect=Exception("Chrome not found")):
        with patch('webbrowser.open_new_tab') as mock_open_new_tab:
            app = runChromeApp('localhost', 8000, (800, 600))
            mock_open_new_tab.assert_called_once_with("http://localhost:8000")
            assert hasattr(app, 'wait')
            assert hasattr(app, 'exit')
            app.wait(None)
            app.exit()

@pytest.mark.asyncio
async def test_my_server_jules():
    from htag.runners.runner import MyServer

    exit_callback = Mock()
    routes = [("/", "handler_function")]

    server = MyServer("localhost",8080,None,False,routes,False,exit_callback)

    with patch('htag.runners.runner.MyServer.jsinteract', "interact('%s')"):
        with patch.object(server, 'hrcreate', return_value=Mock()) as mock_hrcreate:
            server._routes["/"]["hr"] = None
            server.doGet("/", MyApp, ("arg",))
            mock_hrcreate.assert_called_once()
            mock_hrcreate.reset_mock()
            server._routes["/"]["hr"] = Mock(init=("arg",))
            server.doGet("/", MyApp, ("arg",))
            mock_hrcreate.assert_not_called()

@pytest.mark.asyncio
async def test_server_ws_jules():
    from htag.runners.runner import ServerWS

    with patch('htag.runners.runner.start_server', new_callable=AsyncMock) as mock_start_server:
        server = ServerWS("localhost", 8080, None, False, [], False, Mock())
        mock_hr = Mock()
        server._routes['/'] = {'hr': mock_hr}
        server.hrinteract = AsyncMock(return_value=json.dumps({"actions": "test_actions"}))
        await server.run()

        mock_start_server.assert_called_once()
        ws_handler = mock_start_server.call_args[0][1]

        mock_ws = AsyncMock()
        mock_ws.request.path = '/'
        mock_ws.recv.side_effect = ['{"id":1}', None]

        await ws_handler(mock_ws)

        server.hrinteract.assert_awaited_once_with(mock_hr, '{"id":1}')
        mock_ws.send.assert_awaited_with('{"actions": "test_actions"}')

@pytest.mark.asyncio
async def test_server_http_jules():
    from htag.runners.runner import ServerHTTP, HTTPResponse

    with patch('htag.runners.runner.start_server', new_callable=AsyncMock) as mock_start_server:
        server = ServerHTTP("localhost", 8080, None, False, [], False, Mock())
        mock_hr = Mock()
        server._routes['/'] = {'hr': mock_hr, 'handler': Mock()}
        server.hrinteract = AsyncMock(return_value=json.dumps({"actions": "test_actions"}))

        await server.run()

        mock_start_server.assert_called_once()
        routing_handler = mock_start_server.call_args[0][0]

        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.path = "/"
        mock_request.body = b'{"id":1}'

        response = await routing_handler(mock_request)

        server.hrinteract.assert_awaited_once_with(mock_hr, '{"id":1}')
        assert isinstance(response, HTTPResponse)
        assert response.status == 200
        assert "application/json" in response.headers.get("Content-Type")
        assert json.loads(response.content) == {"actions": "test_actions"}

if __name__=="__main__":
    test_default()
    test_runner_instantiation_and_methods_jules()
    test_utility_functions_jules()
    asyncio.run(test_my_server_jules())
    asyncio.run(test_server_ws_jules())
    asyncio.run(test_server_http_jules())