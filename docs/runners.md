# Runners

The 'Runners' is the htag denomination, for some classes provided with htag, to help you to run a **Htag App** in a context. Here are the current provided runners, and could give you ideas of what you want ;-)

**htag** provides officialy 3 runners :

 - Runner : the base one, for desktop app
 - PyScript : the special to be runned in pure html side
 - PyWebView : a specific for desktop using a CEF UI (using [pywebview](https://pywebview.flowrl.com/)) ... (it could be in another htag module soon)

If you want to create an "Android app" (smartphone, tv, etc ...) see [htagapk recipes](https://github.com/manatlan/htagapk))

If you want to create an "Web app" (multiple clients) see [htagweb runner](https://github.com/manatlan/htagweb))

Between 0.90 & 1.0 versions, htag provides the old runners (for compatibility reasons), but they are deprecated and will be removed at 1.0. Here they are:

 - AndroidApp
 - BrowserHTTP
 - BrowserStarletteHTTP
 - BrowserStarletteWS
 - ChromeApp
 - DevApp
 - BrowserTornadoHTTP
 - WinApp

Currently, all are faked/simulated and use the new `Runner` instead (thus, a runner like BrowserStarletteWS, doesn't use starlette anymore, but the new runner home-made server, which is enough robust for one client/user ;-) )





## Runner 'Runner'

This runner can simulate all old runners. All specialized features, that were in some runners only, are all available now. This runner is a pure python server (holding Websocket/HTTP connexions). Things like uvicorn/starlette/tornado were overbloated for a server which can handle one client ;-)

See [Runner](runner.md)

## Runner 'PyScript'
Run everything in client side, thanks to the marvellous [pyscript](https://pyscript.net/). Don't know if there is an utility, but it's possible ;-).
It should run OOTB, everywhere where pyscript runs.

Run your `App` (htag.Tag class), in a HTML file, like this :

```python
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://pyscript.net/releases/2024.10.2/core.css">
    <script type="module" src="https://pyscript.net/releases/2024.10.2/core.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body> loading pyscript ;-)
<script type="py" config='{"packages":["htag"]}'>

###############################################################################
from htag import Tag

class App(Tag.body):
    ...

###############################################################################
from htag.runners import PyScript
PyScript( App ).run()

</py-script>
</body>
</html>
```

[source](https://github.com/manatlan/htag/blob/main/htag/runners/pyscript.py)

**Pros**

 - you only need a browser ;-)
 - Interactions are INPROC.
 - no need of external libs


**Cons**

 - Launching the pyscript environnement can be long.













## Runner 'PyWebView'
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








