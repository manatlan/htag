# Runner



## `__init__( self, tagClass, file, ...properties... )`

It's the Runner constructor

### tagClass:Tag|None = None

It's the tag class you want to be served at "/" path. It's the class which will create the first instance when you run your app.

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

#### port:int = 8000

#### interface = 1
values:
- 1|True -> browser (quit on exit)
- (width,height) -> chromeapp (fallback to browser) (quit on exit),
- 0|False|None -> serve forever

#### reload:bool = False 

#### debug:bool = False

#### http_only:bool = False

#### use_first_free_port:bool = False


## add_route(self,path,handler) -> None


## serve()
