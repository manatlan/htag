# Runners

The 'Runners' is the htag denomination, for some classes provided with htag, to help you to run a **Htag App** in a context. Here are the current provided runners, and could give you ideas of what you want ;-)

For example :

 * "BrowserHTTP" is really adapted to run your htag app with just pure python.
 * "BrowserStarletteHTTP" is the perfect runner during developpement process, because it can autoreload on file changes, and it's easier to follow http interactions.
 * "PyWebView" is the perfect solution, to deliver a gui python app, as a freezed exe (embbeding the pywebview/cef).
 * "ChromeApp" is the perfect solution to deliver a gui python app, with minimal footprints, because it will reuse the installed chrome of the computer.
 * "PyScript" is fun, if you only have a browser (no need of python ;-))

But, in all cases, your **htag app** will run in all theses runners, in the same way !

## AndroidApp
Run a tornado webserver, and open the kivy webview, in an android context, to render the HTag app.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import AndroidApp
AndroidApp( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/androidapp.py)

[tutorial](https://github.com/manatlan/htagapk)

## BrowserHTTP
Run a http server, and open the default browser to render the HTag app.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import BrowserHTTP
BrowserHTTP( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/browserhttp.py)

**Pros**

 - Use only python included battery (no need of others libs)
 - debugging is simple (can see http exchanges in the browser dev tools)

**Cons**

 - the http server is not robust at all

## BrowserStarletteHTTP
Run a http server (using starlette/uvicorn), and open the default browser to render the HTag app.

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

**Cons**

 - need external libs


## BrowserStarletteWS
Run a WS server (using starlette/uvicorn), and open the default browser to render the HTag app.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import BrowserStarletteWS
BrowserStarletteWS( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/browserstarlettews.py)

**Pros**

 - the WS server is (ultra) robust
 - [can use uvicorn reloader](https://github.com/manatlan/htag/blob/main/examples/autoreload.py), useful during dev process !

**Cons**

 - need external libs
 - debugging is not simple (can see ws exchanges are not visible in the browser dev tools)


## ChromeApp
Run a http server (using starlette/uvicorn), and open the default chrome, in [App Mode](https://technastic.com/open-websites-in-application-mode-google-chrome/), to render the HTag app.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import ChromeApp
ChromeApp( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/chromeapp.py)

**Pros**

 - the http server is (ultra) robust
 - debugging is simple (can see http exchanges in the browser dev tools)
 - looks like a cef/electron app, without cef (reuse installed chrome)

**Cons**

 - need external libs
 - need an installed chrome

## PyScript
Run everything in client side, thanks to the marvellous [pyscript](https://pyscript.net/). Don't know if there is an utility, but it's possible ;-).
It should run OOTB, everywhere where pyscript runs.

Run your `App` (htag.Tag class) like this :

```python
from js import window
from htag.runners import PyScript
PyScript( App ).run( window )
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/pyscript.py)

**Pros**

 - you only need a browser ;-)
 - Interactions are INPROC.
 - no need of external libs
 - can handle [multiple htag objects](https://github.com/manatlan/htag/blob/main/examples/pyscript_multi.html) (with url anchors)

**Cons**

 - Setuping the pyscript environnement can be long.

## PyWebWiew
Run everything in a [pywebview](https://pywebview.flowrl.com/) instance. The ideal solution to provide a "python GUI app".

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import PyWebWiew
PyWebWiew( App ).run()
```


[source](https://github.com/manatlan/htag/blob/main/htag/runners/pywebview.py)

**Pros**

 - Interactions are INPROC.

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

**Cons**

 - need external libs

## WebHTTP
Run a http server (using starlette/uvicorn), and serve the htag app to any browser.

Run your `App` (htag.Tag class) like this :

```python
from htag.runners import WebHTTP
WebHTTP( App ).run()
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/webhttp.py)

**Pros**

 - can handle session (multi users)
 - can handle multiple htag objects (with url)
 - the http server is (ultra) robust
 - debugging is simple (can see http exchanges in the browser dev tools)
 - [can use uvicorn reloader](https://github.com/manatlan/htag/blob/main/examples/autoreload.py), useful during dev process !

**Cons**

 - need external libs


## Summary

Like said before ... Htag provides somes [`runners`](https://github.com/manatlan/htag/runners) ootb. But they are just here for the show. IRL: you should build your own, for your needs.

Example :

In my case, I've build my own, as a "htag application web server" : a process which can spawn/manage htag process, and communicate with a front http/ws server, thru unix socket. The "htag web app" communicate with the front http/ws server using websocket if available, or fallback to http. It's pretty solid, and works like a charm. If I reach to make it more generic, I will add another runner for this concept later.
