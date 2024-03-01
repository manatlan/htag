
# Concepts

Here are the concepts, for 1.0 version. (but all is here since 0.8.15)
(For now, some concepts are presented in [tutorial](../tutorial). But here, it's my global plan to make a minimal doc ;-) )

## Technically
**HTag** let you easily build UI elements/widgets (using HTML technologies under the hood), and display them in any things which can render HTML (thru [runners](../runners)).

In fact, it will render it as a SPA, and will manage all interactions for you (between the UI and the python code), without much knowledgement in html/js/css techs.

Everything is done in 3 layers :

* **`Tag`**: the module to build your UI (it's a metaclass to build html/htag components)
* `HRenderer` : the abstraction layer between `Tag` (^) and `Runner` (v) (which make all the magic). You can forget it.
* **`Runner`** : the process which will run the **main tag** (AKA the **htag app**) in a context.

The `Runner` will manage the underlying communications between the UI (the front (python htag > html)), and the python code (the back (python)), in differents manners, depending on the `Runner` which is used. (ex: Some use HTTP only, some use HTTP or WS, some use inproc/direct calls ... depending of the technologies used by the `Runner`)

There are a lot of [runners](../runners), which comes OOTB with [htag](https://pypi.org/project/htag/). Just grab the one which suit your needs. All you need to know is how to build a GUI App with the `htag.Tag`, and it's the purpose of this page ;-)

But the main concept is here: you can developp an **Htag App** which will work anywhere; as a web app, as a desktop app, or as an android app : it will be the same codebase (just depending on the `Runner` context)

It can be seen as a "VueJs|Angular|React" framework on python side; a statefull instance which manage/render htag's components (states changes are handled by the interactions between the front and the back)

## Tag construction

`htag.Tag` is a metaclass helper to build an html tag.

```python
from htag import Tag

mydiv = Tag.div("hello world")
```
`mydiv` will produce a html ouptut as `<div>hello world</div>` ;-)

The firt parameter is the default content of the object, and can be everything (which have a `__str__` method)

Here are some others tag constructions :

``` python
Tag.div(42)                           # --> <div>42</div>
Tag.div()                             # --> <div></div>
Tag.div( "hello " + Tag.b("world") )  # --> <div>hello <b>world</b></div>
Tag.what_you_want("hello")            # --> <what-you-want>hello</what-you-want>
```
. . .

- TODO: (and inherit open/closed (the `**a` trick))
- TODO: (placeholder)

## Tag properties : parent and root
- TODO: (warn root in init !)
- TODO: (strict mode)

## Run javascript
- TODO: [@expose decorator](js_bidirectionnal.md)
- TODO: self.js vs self.call( Js ) (and tag js var)

## Bind events
- TODO: (four ways, chaining bind, chaining Js before/after)
- TODO: (use b'' for javascript)

## Events (in python side)
- TODO: sync/async and yield
- TODO: and stream (adding tag with yield)

## Include statics
- TODO: howto, and shortcuts for js/style
- TODO: and imports trick

## rendering lately vs dynamic
- TODO: main.tag setted as body
- TODO: in render : avoid tag construction -> coz redraw all (now protected in STRICT_MODE)
- TODO: ... And hrenderer/runners (and url queryparams)

## Runners
[url and instanciations](query_params.md)
- TODO: (and state management)
- For now, [See runners](../runners)
