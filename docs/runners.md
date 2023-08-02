# Runners

The 'Runners' is the htag denomination, for some classes provided with htag, to help you to run a **Htag App** in a context. Here are the current provided runners, and could give you ideas of what you want ;-)

For example :

 * [BrowserHTTP](#browserhttp) is really adapted to run your htag app with just pure python.
 * [DevApp](#devapp) is the perfect runner during developpement process, because it autoreloads (and autorefreshs UI) on file changes, and it's easy to follow http interactions in devtools/console of your browser.
 * [PyWebView](#pywebview) is the perfect solution, to deliver a gui python app, as a freezed exe (embbeding the pywebview/cef).
 * [ChromeApp](#chromeapp) is the perfect solution to deliver a gui python app, with minimal footprints, because it will reuse the installed chrome of the computer. (see [WinApp](#winapp) too)
 * [PyScript](#pyscript) is fun, if you only have a browser (no need of python ;-), just html !
 * [WebHTTP](#webhttp) to make real web apps, for many users. Providing session instances

But, in all cases, your **htag app** will run in all theses runners, in the same way !






## AndroidApp
Run a tornado webserver, and open the kivy webview, in an android context, to render the HTag app ([Here you will find recipes](https://github.com/manatlan/htagapk)) ! And it's simple !

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import AndroidApp
AndroidApp( App ).run()
```

**nb**

 - the app should (TODO: test it !) `self.exit()`
 - Understand [query params from url](query_params.md) to instanciate the main htag class

[source](https://github.com/manatlan/htag/blob/main/htag/runners/androidapp.py)









## BrowserHTTP
Run a http server, and open the default browser to render the HTag app. It's the only one in pure python3, and works without any dependancies (except htag ;-)

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import BrowserHTTP
BrowserHTTP( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/browserhttp.py)

**Pros**

 - Use only python included battery (no need of others libs)
 - debugging is simple (can see http exchanges in the browser dev tools)
 - the app can `self.exit()`
 - Understand [query params from url](query_params.md) to instanciate the main htag class

**Cons**

 - the http server is not robust at all







## BrowserStarletteHTTP
Run a http server (using starlette/uvicorn), and open the default browser to render the HTag app. Because it's based on **Starlette**, this runner is an **ASGI HTag App**, which provide [a lot of features](asgi.md)

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import BrowserStarletteHTTP
BrowserStarletteHTTP( App ).run()
```


[source](https://github.com/manatlan/htag/blob/main/htag/runners/browserstarlettehttp.py)

**Pros**

 - the http server is (ultra) robust
 - debugging is simple (can see http exchanges in the browser dev tools)
 - [can use uvicorn reloader](https://github.com/manatlan/htag/blob/main/examples/autoreload.py), useful during dev process !
 - the app can `self.exit()`
 - Understand [query params from url](query_params.md) to instanciate the main htag class


**Cons**

 - need external libs







## BrowserStarletteWS
Run a WS server (using starlette/uvicorn), and open the default browser to render the HTag app. Because it's based on **Starlette**, this runner is an **ASGI HTag App**, which provide [a lot of features](asgi.md)

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import BrowserStarletteWS
BrowserStarletteWS( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/browserstarlettews.py)

**Pros**

 - the WS server is (ultra) robust
 - [can use uvicorn reloader](https://github.com/manatlan/htag/blob/main/examples/autoreload.py), useful during dev process !
 - and [a lot of features](asgi.md), because it's astarlette/asgi.
 - the app can `self.exit()`
 - Understand [query params from url](query_params.md) to instanciate the main htag class


**Cons**

 - need external libs
 - debugging is not simple (can see ws exchanges are not visible in the browser dev tools)








## ChromeApp
Run a http server (using starlette/uvicorn), and open the default chrome, in [App Mode](https://technastic.com/open-websites-in-application-mode-google-chrome/), to render the HTag app.
(See [WinApp](#winapp), another variant)

On MS Windows : just double click your `.pyw`, and it will run a chrome app mode (windowed app), and when you close the windowed app, it will close all. And if you put a favicon (link tag), the icon is used in the window, and in the windows task bar... neat (there are no more any other python process spawned in the windows task bar !

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import ChromeApp
ChromeApp( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/chromeapp.py)

**Pros**

 - perfect on MS Windows platforms, as `.pyw` files
 - it closes the server side when windowed app is closed !!
 - the http server is (ultra) robust
 - looks like a cef/electron app, without cef (reuse installed chrome)
 - the app can `self.exit()`
 - and [a lot of features](asgi.md), because it's astarlette/asgi.
 - Understand [query params from url](query_params.md) to instanciate the main htag class
 - you can define the size of the window (`.run( size=(1024,600) )`)

**Cons**

 - need external libs
 - need an installed chrome







## DevApp
This is the perfect runner for development process (internally, it runs a WS server (using starlette/uvicorn), and open the default browser to render the HTag app. Because it's based on **Starlette**, this runner is an **ASGI HTag App**, which provide [a lot of features](asgi.md))

But it provides features like :

 - Hot reloading (reload the code, and the UI automatically)
 - js log (in devtools/console)
 - Display full python error (tracebacks)
 - but CAN'T use `self.exit()` (coz uvicorn/reloader is hard to quit, but in the future : it should be possible)
 - and [a lot of features](asgi.md), because it's astarlette/asgi.
 - Understand [query params from url](query_params.md) to instanciate the main htag class

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import DevApp
app=DevApp( App )
if __name__ == "__main__":
    app.run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/devapp.py)

It should'nt be used in production env. But it's perfect to develop your htag app easily !









## PyScript
Run everything in client side, thanks to the marvellous [pyscript](https://pyscript.net/). Don't know if there is an utility, but it's possible ;-).
It should run OOTB, everywhere where pyscript runs.

Run your `App` (htag.Tag class), in a HTML file, like this :

```python
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
    <script defer src="https://pyscript.net/latest/pyscript.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <py-config>
    packages = ["htag"]
    </py-config>    
</head>
<body> loading pyscript ;-)
<py-script>
###############################################################################
from htag import Tag

class App(Tag.body):
    ...

###############################################################################
from htag.runners import PyScript
from js import window
PyScript( App ).run( window )

</py-script>
</body>
</html>
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/pyscript.py)

**Pros**

 - you only need a browser ;-)
 - Interactions are INPROC.
 - no need of external libs
 - Understand [query params from url](query_params.md) to instanciate the main htag class


**Cons**

 - Launching the pyscript environnement can be long.













## PyWebView
Run everything in a [pywebview](https://pywebview.flowrl.com/) instance. The ideal solution to provide a "python GUI app".

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import PyWebView
PyWebView( App ).run()
```


[source](https://github.com/manatlan/htag/blob/main/htag/runners/pywebview.py)

**Pros**

 - Interactions are INPROC.
 - the app can `self.exit()`


**Cons**

 - til pywebview [doesn't support async calls](https://github.com/r0x0r/pywebview/issues/867), full htag features (async) will not be available ;-(
 - need external libs











## BrowserTornadoHTTP
Run a http server (using tornado), and open the default browser to render the HTag app.
(if you want to use another webserver ;-))

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import BrowserTornadoHTTP
BrowserTornadoHTTP( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/browsertornadohttp.py)

**Pros**

 - the http server is robust
 - debugging is simple (can see http exchanges in the browser dev tools)
 - the app can `self.exit()`
 - and [a lot of features](asgi.md), because it's astarlette/asgi.
 - Understand [query params from url](query_params.md) to instanciate the main htag class

**Cons**

 - need external libs













## WebHTTP
Run a http server (using starlette/uvicorn), and serve the htag app to any browser.
Because it's based on **Starlette**, this runner is an **ASGI HTag App**, which provide [a lot of features](asgi.md)

As it's a webserver, and unlike others : you can have many clients, so it's a different beast ;-)

**NEW** See [htagweb](https://github.com/manatlan/htagweb), for a better solution !

It manages a http session (with a cookie), and the session is available, per user, in `request.session`, or `<htag_instance>.session` (sessions are server-side). But, you can have only one instance of a htag Tag class, per user. (and like others, if you hit F5/refresh, it will reuse the current instance (not recreate it!)). The re-creation of the instance is based on the url/path (you'll need to change query_params, for example), and so ; the newest will replace the old one, so the memory stay "acceptable". And, of course, you can have many htag class managed by many endpoints. (see: [asgi things](asgi.md))

HTag wasn't designed (at start) to be served on a webserver (with many clients), But this solution is completly usable, with this kind of runner.

Of course, the session is usable with starlette/authlib flow to identify a user with an oauth2 flow (ex: google login) (TODO: give an example).

The session timeout is settable when you instanciate the "WebHTTP" runner. (ex: `WebHTTP( Klass , timeout=10*60)`, but by default it's 10 minutes). When the session expires, it clears all data on server side, for the user.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import WebHTTP
WebHTTP( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/webhttp.py)

**Pros**

 - can handle session (**multiple users**)
 - the http server is (ultra) robust
 - debugging is simple (can see http exchanges in the browser dev tools)
 - [can use uvicorn reloader](https://github.com/manatlan/htag/blob/main/examples/autoreload.py), useful during dev process !
 - and [a lot of features](asgi.md), because it's starlette/asgi.
 - the app can't `self.exit()` (for security reasons)
 - Understand [query params from url](query_params.md) to instanciate the main htag class


**Cons**

 - need external libs



## WebWS
See [WebHTTP](#webhttp). It's the same thing, but on websocket, instead of http.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import WebWS
WebWS( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/webws.py)


## WinApp
Run a http server (using tornado), and open the default installed chrome, in [App Mode](https://technastic.com/open-websites-in-application-mode-google-chrome/), to render the HTag app.
(See [ChromeApp](#chromeapp), another variant)

On MS Windows : just double click your `.pyw`, and it will run a chrome app mode (windowed app), and when you close the windowed app, it will close all. And if you put a favicon (link tag), the icon is used in the window, and in the windows task bar... neat (there are no more any other python process spawned in the windows task bar !

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import WinApp
WinApp( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/winapp.py)

**Pros**

 - perfect on MS Windows platforms, as `.pyw` files
 - it closes the server side when windowed app is closed !!
 - the http server is robust
 - looks like a cef/electron app, without cef (reuse installed chrome)
 - the app can `self.exit()`
 - Understand [query params from url](query_params.md) to instanciate the main htag class
 - you can define the size of the window (`.run( size=(1024,600) )`)

**Cons**

 - Not suited at all for development : debugging is complex (everything is in the socket)
 - need external libs (just tornado)
 - need an installed chrome











## Summary

 | Features :                             | AndroidApp | BrowserHTTP | BrowserStarletteHTTP | BrowserStarletteWS | ChromeApp | DevApp | PyScript | PyWebView | BrowserTornadoHTTP | WebHTTP | WinApp  |
 |:---------------------------------------|:----------:|:-----------:|:--------------------:|:------------------:|:---------:|:------:|:--------:|:---------:|:------------------:|:-------:|:-------:|
 | Work without external libs             |            | yes         |                      |                    |           |        | yes      |           |                    |         |         |
 | Work on android                        | yes        |             |                      |                    |           |        | yes      |           |                    |         |         |
 | Is ASGI (with Starlette/uvicorn        |            |             | yes                  | yes                |           | yes    |          |           |                    | yes     |         |
 | Can `self.exit()`                      | (should)   | yes         | yes                  | yes                | yes       | no ;-( |          | yes       |  yes               | no!     |  yes    |
 | Can use url query params               | yes        | yes         | yes                  | yes                | yes       | yes    | yes      |           |  yes               | yes     |  yes    |


Htag provides somes [`runners`](https://github.com/manatlan/htag/runners) ootb. But they are just here for the show. IRL: you should build your own, for your needs.

**Example:**

In my case, I've build my own, as a "htag application web server" : a process which can spawn/manage htag process, and communicate with a front https/wss server, thru unix socket. The "htag web app" communicate with the front https/wss server ~~using websocket if available, or fallback to http~~. It's pretty solid, and works like a charm. ~~If I reach to make it more generic, I will add another runner for this concept later~~.

Now, it's real, it's [htagweb](https://github.com/manatlan/htagweb) !
