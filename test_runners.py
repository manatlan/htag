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

@pytest.mark.asyncio
async def test_runner_run_ws_mode_jules():
    from htag.runners import Runner
    with patch('asyncio.get_event_loop') as mock_get_loop, \
         patch('webbrowser.open_new_tab'), \
         patch('htag.runners.runner.isFree', return_value=True), \
         patch('htag.runners.runner.ServerWS') as MockServerWS:

        mock_loop = mock_get_loop.return_value
        mock_loop.run_forever.side_effect = KeyboardInterrupt() # prevent blocking
        with patch('os._exit'):
            runner = Runner(MyApp, interface=1)
            runner.run()
            mock_loop.create_task.assert_called_once() # watchdog was created

@pytest.mark.asyncio
async def test_runner_run_http_mode_jules():
    from htag.runners import Runner
    with patch('asyncio.get_event_loop') as mock_get_loop, \
         patch('webbrowser.open_new_tab'), \
         patch('htag.runners.runner.isFree', return_value=True), \
         patch('htag.runners.runner.ServerHTTP'):

        mock_loop = mock_get_loop.return_value
        mock_loop.run_forever.side_effect = KeyboardInterrupt() # prevent blocking
        with patch('os._exit'):
            runner = Runner(MyApp, http_only=True, interface=True)
            runner.run()
            mock_loop.create_task.assert_not_called() # no watchdog

@pytest.mark.asyncio
async def test_runner_with_chrome_app_jules():
    from htag.runners import Runner
    with patch('asyncio.get_event_loop') as mock_get_loop, \
         patch('htag.runners.runner.runChromeApp') as mock_run_chrome, \
         patch('htag.runners.runner.isFree', return_value=True), \
         patch('htag.runners.runner.ServerWS'):

        mock_loop = mock_get_loop.return_value
        mock_loop.run_forever.side_effect = KeyboardInterrupt()
        with patch('os._exit'):
            runner = Runner(MyApp, interface=(800, 600))
            runner.run()
            mock_run_chrome.assert_called_with("127.0.0.1", 8000, (800, 600))


def test_runner_init_with_file_jules():
    from htag.runners import Runner
    with patch('htag.runners.commons.SessionFile') as mock_session_file:
        runner = Runner(MyApp, file="/path/to/session.json")
        assert runner.session == mock_session_file.return_value

@pytest.mark.asyncio
async def test_runner_bad_interface_jules():
    from htag.runners import Runner
    with patch('asyncio.get_event_loop'), \
         patch('htag.runners.runner.isFree', return_value=True), \
         patch('htag.runners.runner.ServerWS'):
        runner = Runner(MyApp, interface="invalid")
        with pytest.raises(Exception, match="Not a good 'interface' !"):
            runner.run()

@pytest.mark.asyncio
async def test_runner_port_search_jules():
    from htag.runners import Runner
    with patch('htag.runners.runner.isFree', side_effect=[False, False, True]) as mock_is_free, \
         patch('asyncio.get_event_loop') as mock_get_loop:

        mock_loop = mock_get_loop.return_value
        mock_loop.run_forever.side_effect = KeyboardInterrupt() # prevent blocking
        with patch('os._exit'):
            runner = Runner(MyApp, use_first_free_port=True)
            assert runner.port == 8000
            runner.run()
            assert runner.port == 8002
            assert mock_is_free.call_count == 3

def test_reload_no_module_jules():
    from htag.runners.runner import reload
    with patch('inspect.getmodule', return_value=None):
        reloaded_class = reload(MyApp)
        assert reloaded_class == MyApp

def test_hrcreate_no_dev_jules():
    from htag.runners.runner import MyServer
    # Non-dev mode
    server_no_dev = MyServer("localhost", 8080, None, False, [], dev=False, exit_callback=Mock())
    hrenderer_no_dev = server_no_dev.hrcreate(MyApp, "js", ((),{}))
    assert not hrenderer_no_dev.fullerror

    # Dev mode
    server_dev = MyServer("localhost", 8080, None, False, [], dev=True, exit_callback=Mock())
    hrenderer_dev = server_dev.hrcreate(MyApp, "js", ((),{}))
    assert hrenderer_dev.fullerror

    # Check that dev mode adds exactly 2 statics (template and script)
    assert len(hrenderer_dev._statics) == len(hrenderer_no_dev._statics) + 2

@pytest.mark.asyncio
async def test_server_ws_handler_exception_jules():
    from htag.runners.runner import ServerWS
    ws = AsyncMock()
    ws.request.path = "/"
    ws.recv.side_effect = [Exception("test exception"), None]

    server = ServerWS("localhost", 8080, None, False, [("/", Mock())], False, Mock())
    server._routes["/"]["hr"] = Mock()

    with patch("htag.runners.runner.start_server") as mock_start:
        await server.run()
        handler_ws = mock_start.call_args[0][1]
        await handler_ws(ws)
        ws.send.assert_awaited_with('{}')

def test_runner_stop_with_chromeapp_jules():
    from htag.runners import Runner
    runner = Runner(MyApp)
    chromeapp_mock = Mock()
    runner.chromeapp = chromeapp_mock
    with patch('os._exit') as mock_exit:
        runner.stop()
        chromeapp_mock.exit.assert_called_once()
        mock_exit.assert_called_once_with(0)

def test_runner_init_with_invalid_tag_jules():
    from htag.runners import Runner
    class NotATag:
        pass
    with pytest.raises(AssertionError):
        Runner(NotATag)

@pytest.mark.asyncio
async def test_my_server_routing_jules():
    from htag.runners.runner import MyServer, HTTPResponse

    async def handler_with_params(request):
        return HTTPResponse(200, f"params:{request.path_params}")

    async def handler_get(request, handler):
        return await handler(request)

    async def handler_post(request, hr):
        if request.path == "/error_post":
            raise ValueError("POST error")
        return HTTPResponse(200, "ok post")

    async def error_handler_get(request):
        raise ValueError("GET error")

    async def error_handler_params(request):
        raise ValueError("params error")

    routes = [
        ("/items/{id}", handler_with_params),
        ("/direct", lambda req: HTTPResponse(200,"ok")),
        ("/error_get", error_handler_get),
        ("/error_params/{id}", error_handler_params),
        ("/error_post", lambda req: HTTPResponse(200,"ok")),
    ]
    server = MyServer("localhost", 8080, None, False, routes, False, Mock())
    server._routes["/error_post"]["hr"] = Mock()

    with patch("htag.runners.runner.start_server", new_callable=AsyncMock) as mock_start_server:
        await server.server(handler_get, handler_post, None)
        routing = mock_start_server.call_args.args[0]

        # Test GET path params
        request = Mock()
        request.path = "/items/123"
        request.method = "GET"
        response = await routing(request)
        assert response.status == 200
        assert b"params:{'id': '123'}" in response.content

        # Test not found
        request.path = "/notfound"
        response = await routing(request)
        assert response.status == 404

        # Test bad method on direct route
        request.path = "/direct"
        request.method = "PUT"
        response = await routing(request)
        assert response.status == 400

        # Test handler exception on direct route
        request.path = "/error_get"
        request.method = "GET"
        response = await routing(request)
        assert response.status == 500
        assert b"GET error" in response.content

        # Test handler exception on route with params
        request.path = "/error_params/1"
        request.method = "GET"
        response = await routing(request)
        assert response.status == 500
        assert b"params error" in response.content

        # Test POST handler exception
        request.path = "/error_post"
        request.method = "POST"
        response = await routing(request)
        assert response.status == 500
        assert b"POST error" in response.content

if __name__=="__main__":
    test_default()
    test_runner_instantiation_and_methods_jules()
    test_utility_functions_jules()
    asyncio.run(test_my_server_jules())
    asyncio.run(test_server_ws_jules())
    asyncio.run(test_server_http_jules())
    asyncio.run(test_runner_run_ws_mode_jules())
    asyncio.run(test_runner_run_http_mode_jules())
    asyncio.run(test_runner_with_chrome_app_jules())
    asyncio.run(test_my_server_routing_jules())

deprecated_runners_data = [
    ("BrowserHTTP", {"http_only": True}),
    ("BrowserStarletteHTTP", {"http_only": True}),
    ("BrowserStarletteWS", {}),
    ("DevApp", {"debug": True, "reload": True, "use_first_free_port": True}),
    ("ChromeApp", {"use_first_free_port": True}),
    ("WinApp", {"use_first_free_port": True}),
    ("BrowserTornadoHTTP", {"http_only": True}),
]

@pytest.mark.parametrize("runner_name, runner_args", deprecated_runners_data)
def test_deprecated_runners_jules(runner_name, runner_args):
    from htag import runners

    with patch("htag.runners.Runner.__init__") as mock_runner_init, \
         patch("htag.runners.Runner.run") as mock_runner_run, \
         patch("htag.runners.deprecated") as mock_deprecated:

        RunnerClass = getattr(runners, runner_name)
        instance = RunnerClass(MyApp)

        mock_deprecated.assert_called_once_with(instance)

        mock_runner_init.assert_called_once()
        call_args, call_kwargs = mock_runner_init.call_args

        assert call_args[0] is instance
        assert call_args[1] is MyApp
        assert call_args[2] is None # file is always None

        assert call_kwargs == runner_args

        # Test the run method
        if runner_name in ["ChromeApp", "WinApp"]:
            instance.run(size=(100,100))
            assert instance.interface == (100,100)
        else:
            instance.run(openBrowser=False)
            assert instance.interface == 0

        mock_runner_run.assert_called_once()


def test_android_app_runner_jules():
    from htag import runners
    with patch("htag.runners.Runner.__init__") as mock_runner_init, \
         patch("htag.runners.Runner.run") as mock_runner_run, \
         patch("htag.runners.deprecated") as mock_deprecated:

        instance = runners.AndroidApp(MyApp)
        mock_deprecated.assert_called_once()

        mock_runner_init.assert_called_once()
        call_args, call_kwargs = mock_runner_init.call_args

        assert call_args[0] is instance
        assert call_args[1] is MyApp
        assert call_args[2] is None # file is None

        assert call_kwargs == {"interface": 0, "port": 12458, "use_first_free_port": False}

        instance.run()
        mock_runner_run.assert_called_once()

def test_runner_import_error_jules():
    import sys
    with patch.dict('sys.modules', {'htag.runners.pywebview': None}):
        # Force a reload of the module to trigger the import error
        importlib.reload(importlib.import_module("htag.runners"))
        from htag import runners
        with pytest.raises(Exception):
            runners.PyWebView(MyApp)
    # Restore the original state
    importlib.reload(importlib.import_module("htag.runners"))