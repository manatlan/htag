# tag.update()

This feature add a "send from backend to frontend" capacity, which can only work with
[Runners](runners.md) which have a "permanent connexion" with front end (think websocket)

Note that this feature will not work, in this cases:

 - When the Runner is in `http_only` mode (because this feature use websocket only) !
 - With [PyWebView](runners.md#PyWebView) runner, because [pywebview](https://pywebview.flowrl.com) doesn't support async things.

It opens a lot of powers, and real time exchanges (see `examples/new_*.py`) ! and works for [htagweb](https://github.com/manatlan/htagweb) & [htagapk](https://github.com/manatlan/htagapk) too.

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
