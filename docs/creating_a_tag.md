# Creating a Tag : the complete guide

If you come from [domonic](https://github.com/byteface/domonic) or [brython](https://brython.info/static_doc/fr/create.html) : htag borrows the best ideas from them.

## The basics

### At construction time
A Tag (htag's Tag) is a helper to let you build easily html representation of an object.

The signature of the helper could be: `Tag.<html>( <content_or_None>, **attrs ) -> htag instance`
 * Where `<html>` can be "div","span","input", .. or whatever you want (it will be the html tag representation)
 * Where `<content_or_None>` can be None or whatever which is str'able (list are accepted too)
 * Where `attrs` can be any attributs to specialize the creation (see later)


```python
from htag import Tag

print( Tag.div("hello world") )
```
Will generate `<div>hello world</div>` ... easy ;-)

If you want to set html attributs, prefix them with '_'

```python
print( Tag.div("hello world", _style="background:yellow") )
```
Will generate `<div style="background:yellow">hello world</div>` ;-)

It will work for every kind of html attributs, and events too

```python
print( Tag.div("hello world", _onclick="alert(42)") )
```
Will generate `<div onclick="alert(42)">hello world</div>` ;-)

You can construct whatever tag you want ...

```python
print( Tag.my_tag("hello world", _class="mine") )
```
Will generate `<my-tag class="mine">hello world</my-tag>` (notice that the `_` is replaced by `-` ;-)

```python
print( Tag.span("hello world", _val=12, _checked=True) )
```
Will generate `<span val="12" checked>hello world</span>` !

It's simple ;-)

But you can init some instance properties at construction time ...
```python
tag = Tag.span("hello world", value=12, _value=42 )
print( tag )
```
Will generate `<span value="42">hello world</span>`, but the instance var (here `tag`) will contain 12 ( tag.value==12 ) !
So `_value` is an html attribut ... whereas `value` is an instance property (on python side only). It's important to understand the difference.

Take a break, and medit on that ;-)

You can compose tags ...
```python
Tag.div( Tag.span("hello")+" "+Tag.b("world") )
# or
Tag.div( [Tag.span("hello")," ",Tag.b("world")] )
```
it's basically the same thing ^^

### Post construction time

all this variables are usable/settable post construction time.
```python
tag = Tag.span("hello world", value=12, _value=42 )
assert tag["value"]==42
assert tag.value==12
```
html attributs are in the dictitem of the tag ! Whereas the instance properties are in the instance ;-)

So you can do that:
```python
tag = Tag.a("hello world")
tag["onclick"]="alert(42)"
```
And you can compose them like that :

```python
div=Tag.div()
div.add( Tag.span("hello") )
div.add( " " )
div.add( Tag.b("world") )
```

but there are operators (`+=` (prefer) or `<=` (brython style)), to simplify that :
```python
div = Tag.div()
div += Tag.span("hello")
div += " "
div += Tag.b("world")
```

easy, no ?

BTW, you can use the `with/as` statement, like that (since htag>=0.13):

```python
with Tag.div() as t:
    t += Tag.span("hello")
    t += " "
    t += Tag.b("world")
    t["style"]="background:#EEE"
```



### IRL (in A Runner Context)

An important thing to understand, is that a Tag renders differently when used in a runner (TODO:LINK).
AS you see before, the tags are rendered without attributs 'id'. But, IRL, when using in a htag runner context, all tags are rendered with an html id attribut (it's the main reason why you can't set an `_id` at runtime !). Htag's runner manage all the tags, with theirs ids: it's the core feature, to be able to keep states/rendering between the gui/client_side and the back/python ;-)

When used in a Runner Context, some specials properties are setted on a Tag.
 * `root` : Contains the instance of the main tag (AKA the one drived by the HTag's Runner)
 * `parent` : Contains the instance of the parent tag (AKA the one which had added it)

The `root` is very usefull, to refer global properties/methods from a single place. The `parent` can be usefull in complex components which involve other tree components.

But **BE AWARE** : theses properties are only setted at rendering time ! Not a construction time : in others terms -> you can't use them in a construction phase ! It really important to understand that!

### Inherit a Tag

It's really the main goal of htag : be able to create feature rich components in python style, to be reusable in others apps.

here is a simple div construction:
``` python
Tag.div('hello',_style="background:red")
```

Here is the same, using inheritance (to create a `Div` class) :

``` python
class Div(Tag.div):
    def init(self):
        self += "hello"
        self["style"]="background:red"
```
Both rendering exactly the same kind of result.

Here, you will notice that it uses a special constructor (`init`) in place of the real python constructor (`__init__`). It's just to simplify the process. If you want to use the real python constructor, you can do (but it's longer):

``` python
class Div(Tag.div):
    def __init__(self):
        super().__init__()
        self += "Hello world"
        self["style"]="background:red"
```
It produces exactly the same kind of result.

Now, when you want to use your new component, it's as simple as always :

``` python
class App(Tag.body):
    def init(self):
        self += Div()
```

Now, an important thing to understand : this component 'Div' is said "closed", because you can't specialize it (with html attributs, or instance properties) at construction time.
You can't reuse it like that:

``` python
class App(Tag.body):
    def init(self):
        self += Div(_class="myclass")   # will throw an exception (because it's closed)
```

Because 'Div' doens't accept something in its constructor. So we say that it's "closed".

If you wanted to make you component "opened" (by opposite : to accept html attributs, or instance properties), you should declare it like that :
``` python
class Div(Tag.div):
    def init(self,**a):     # notice the '**a' !
        self += "hello"
        self["style"]="background:red"
```

With classical python constructor it should be :
``` python
class Div(Tag.div):
    def __init__(self, **a):  # notice the '**a' !
        super().__init__(**a) # notice the '**a' !
        self += "Hello world"
        self["style"]="background:red"
```

It's good practice, to create its components in a "opened" way (to be able to customized them later). But sometimes, it makes sense to refuse customization.

BTW, keep in mind, that in all cases ("opened" or "closed"), you can customize them after creation.
``` python
class App(Tag.body):
    def init(self):
        div=Div()
        div["class"]="myclass"  # <- like that
        self += div
```

### Create a dynamic tag (using a `render(self)` method)

You can create a component which will auto render itself on changes. This kind of component is neat for small component. This kind of component are named "dynamic" component, and to be a dynamic component : it must implement a `render(self) -> None`, which will redraw all its content.

A simple example:
```python
class Starrer(Tag.div):
    def init(self,value=0):
        self.value=value

        def inc(v):
            self.value+=v

        self.bless = Tag.Button( "-", _onclick = lambda o: inc(-1) )
        self.bmore = Tag.Button( "+", _onclick = lambda o: inc(+1) )

    def render(self):
        self.clear()
        self += self.bless + self.bmore + ("⭐"*self.value)
```

**IMPORTANT**: AVOID USING `Tag.<html>(content,**kargs)` IN A render() METHOD !!!!!!! (avoid creating new tag instance, because it will create new instance (new ids), and force rendering at each interaction)

See [Example c30](https://htag.glitch.me)

## Creating a "PlaceHolder" Tag

A placeholder tag : is a Tag "without outerHTML", It has no html representation from itself. And its rendering depends on its childs.

TODO: say more ;-)

## Creating a Tag generatior (yield'ing content)

Sometimes, it can be usefull to render on-demand. Imagine that you want to populate a big list, it will be impossible (or very long). **HTag** provide a way to do that, to avoid to draw all the html in one interaction. It can render by fragment, using the `yield` statement.

TODO: say more ;-)

See [Example c90](https://htag.glitch.me)

... TODO ...
