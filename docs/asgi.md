# With an ASGI Runner

Theses runners [BrowserStarletteHTTP](https://manatlan.github.io/htag/runners/#browserstarlettehttp), [BrowserStarletteWS](https://manatlan.github.io/htag/runners/#browserstarlettews) and [WebHTTP](https://manatlan.github.io/htag/runners/#webhttp)
provides an [ASGI](https://asgi.readthedocs.io/en/latest/) HTag runner, which is basically an instance of a [Starlette](https://www.starlette.io/) class. So, you can use
all asgi/starlette features OOTB.

## You can use the uvicorn command line

Admit that you have this python file `myapp.py`

```python
class App(Htag.div):
    ...

app = BrowserStarletteHTTP(App)
```

You can start the server part, from command line, with :

`uvicorn myapp:app`


## You can use the uvicorn reloader

Uvicorn can restart the server on file changes.

### Programmaticaly

```python
class App(Htag.div):
    ...

app = BrowserStarletteHTTP(App)

if __name__=="__main__":
    uvicorn.run(app,reload=True)
```


### by using the command line

You can start the server part, in autoreload mode, from command line, with :

`uvicorn myapp:app --reload`


## You can setup new routes

```python
class App(Htag.div):
    ...

app = BrowserStarletteHTTP(App)
app.add_route("/style.css", mymethod, methods=["GET",])
```
