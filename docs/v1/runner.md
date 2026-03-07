# Runner

A minimal doc ... there are a lot to say more. But this page will evolve soon.

## `__init__( self, tagClass, file, ...properties... )`

It's the Runner constructor

### tagClass:Tag|None = None

It's the tag class you want to be served at "/" path. It's the class which will be used to create the first instance when you run your app.

A common pattern is :
```python
from htag import Tag

class App(Tag.body):
    ...

if __name__ == "__main__":
    from htag.runners import Runner
    Runner(App).run()
```
if you don't provide it, ensure that you `add_route` to the home path "/" (if you want to show something when you run your app)

### file:str|None = None

Here you can set a filepath to a json/file, if you want to persist your session. Currently it's a json serialization, so ensure that objects you put in session are json serializable


### properties:

Theses properties can be set at contructor time, but are instance properties too (can be set after contructor time).

#### host:str = "127.0.0.1"

The IP of the host, by default it's localhost. But can be "" (empty string) to listen world wild (interest ?).

#### port:int = 8000

The port of the HTTP/WS transport.

#### interface = 1

It's the more ambiguous parameter, it can takes 3 values  :

If it's 0|False|None -> it will serve forever, without running the UI part (kind of headless mode). And the server will never quit !

If it's 1|True|None -> it will start the UI interface (start the default browser to "/" path). And the server will autoquit if there are no more interactions (closing the tab -> close the server)

If it's a tuple (width,height) -> it will start a chrome app in app mode (chrome in headless mode), using the defined width/height. If it can't (because you don't have chrome on your computer), it will start the default browser. And the server will autoquit if there are no more interactions (closing the app -> close the server)

example: running in "chrome app mode" (here in a window sized 640x480):

```python
...

class App(Tag.body):
    ...

if __name__=="__main__":
    from htag.runners import Runner
    Runner(App,interface=(640,480)).run()
```

#### reload:bool = False 

To be able to "reload" (recreate) the instances. Can be really useful during dev process !!!
Note that the reloading mechanism only works great when the "App part" is in another file, from the "Runner part" (to be able to reload by module).

So when you hit F5/refresh : it will recreate instances at each refresh ! (in contrario of the default, which always reuse the last instances)

#### debug:bool = False

It's a mechanism which will override the javascript `window.error = function() {}`, to display a popup when exception comes. Can be really useful during dev process. (in the near future, it will display the exchanges in "browser debug tools / console.log", like previous )

#### http_only:bool = False

Can be used to force the exchange to be HTTP only (no websocket!) ... (interest ?)

When it's HTTP ONLY : the [tag.update](tag_update.md) feature can't work.

#### use_first_free_port:bool = False

It's a mechanism to run the "runner part" in all cases ! It will use the next free port available if the current one is already used. It can be useful in some cases.

## `add_route(self,path:str,handler) -> None`

This method let you create a a new route to be able to serve:
- another Tag Class (using `self.handle(request, tagClass) -> HTTPResponse`, see below)
- another http ressource (ex: a jpg, png, html, js ...)

### To serve another Tag Class, a common pattern is :
```python
from htag import Tag

class App(Tag.body):
    ...

class App2(Tag.body):
    ...

if __name__ == "__main__":
    from htag.runners import Runner
    app=Runner(App)
    
    app.add_route( "/other", lambda request: app.handle(request, App2 ) )

    app.run()
```

When serving a Tag Class, you can't set "path parameters" (things like '/item/{idc}') in the route ! But you can get the [query parameters](query_params.md) of the url, to initialize your init constructor of your Tag class. Note that "query parameters" are also available for your default home route ("/").

### To serve an http ressource, a common pattern is :
```python
from htag import Tag

class App(Tag.body):
    ...

if __name__ == "__main__":
    from htag.runners import Runner, HTTPResponse
    app=Runner(App)
    
    async def handlerItem( request ):
        idx=request.path_params.get("idx",0)        
        txt=request.query_params.get("txt","???")
        return HTTPResponse(200,"Number %d (txt=%s)" % (idx,txt))

    app.add_route( "/item/{idx:int}", handlerItem )

    app.run()
```

Note that `request` have 2 dict property :

 - `path_params` : to expose path parameters, when defined in routes (as starlette.add_route does)
 - `query_params` : to expose query parameters (ex: https://example.com/item/42?a=42&b=toto -> {"a":"42","b":"toto"})


Note that path params can be :

 - "/item/{idx}" : idx will be str.
 - "/item/{idx:str}" : idx will be str.
 - "/item/{idx:int}" : idx will be int.
 - "/item/{idx:path}" : idx will be the rest of the path (with url "/item/box/1", idx will be 'box/1')


## `handle(self, request, tagClass ) -> HTTPResponse`

It's an internal method, but can be used with `self.add_route(path,request)` (see upper).
