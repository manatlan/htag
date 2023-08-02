# tag.update()

This is a new feature (post 0.10.0), which can broke the compatibility of a "same htag app works everywhere".
This feature add a "send from backend to frontend" capacity, which can only work with
[Runners](runners.md) which have a "permanent connexion" with front end (think websocket).

Til now, **htag** could only make interactions (actions from frontend to backend); It was always
the frontend who call the backend. With this feature, the backend can communicate to frontend.
And it's only possible if the communication canal is persistant !

Runners compatibles are :

 - [BrowserStarletteWS](runners.md#BrowserStarletteWS), because based on websocket!
 - [DevApp](runners.md#DevApp), because based on websocket!
 - [ChromeApp](runners.md#ChromeApp), because based on websocket!
 - [WinApp](runners.md#WinApp), because based on websocket!
 - [PyScript](runners.md#PyScript), because internal calls!
 - [WebWS](runners.md#WebWS), because based on websocket!
 - [htagweb.HtagServer](https://github.com/manatlan/htagweb), because based on websocket!

All others are not compatibles, because they mainly use `http` between front and back. And
[PyWebView](runners.md#PyWebView) is not compatible too, because [pywebview](https://pywebview.flowrl.com) doesn't support async things. [htagweb.WebServer & htagweb.WebServerWS](https://github.com/manatlan/htagweb) couldn't support this feature too !

So, an "htag app" which use `tag.update()` can only work correctly in thoses runners. In the others,
or if you want to make it fully compatible : no other solutions than implement a "polling system" (a js
`setInterval` which interact with a python method, to redraw things).

But if you target a runner, based on websocket communications, you can use this feature. And it opens a lot
of powers, and real time exchanges (see `examples/new_*.py`) !

Use this only if you understand what you do ;-)

## Use cases

`tag.update()` is a coroutine, so you should use it in a coroutine only. It returns True/False depending
on the capacity to update in realtime. (with http's runners : it will always return False)

Here is an async method of an htag component (runned with a `asyncio.ensure_future( self.do_something() )`):
```python

    async def do_something(self):
        self += "hello"
        isUpdatePossible = await self.update()

```

Note that, the "first updates" can return False, while the websocket is not really connected. And will return
True when it's done.
