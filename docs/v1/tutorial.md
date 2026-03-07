# Tutorial

## Construction

`htag.Tag` is the basic object, and the only one you'll need to use, to build an htag app. The simplest htag app could be :

```python
from htag import Tag

class App(Tag.div): #<= define the html tag container of the app
    """ This is the most simple htag component """

    def init(self):
        # I'm just a div'tag, with a textual node content "hello world"
        self <= "Hello world"   # shortcut for self.add("Hello world")

if __name__=="__main__":
    from htag.runners import Runner
    Runner( App ).run()    # <= this is the runner

```

As you can notice, it uses the simplest constructor `init()`, to construct itself (best practice). But could be replaced by the real form too:

```python
    def __init__(self, **kwargs):
        # I'm just a div'tag, with a textual node content "hello world"
        super().__init__(**kwargs)
        self <= "Hello world"   # shortcut for self.add("Hello world")
```

The simplest form avoid you to deal with the real construction phase under the hood. Because `kwargs` are used to define html attributs (or instance properties) from the ground.

!!! note "Main Tag is always rendered as a body'tag"
    Although `App` is declared as a `Tag.div`, it will be rendered as a body'tag, because it's the main Tag (the one which is drived by the runner)


Here is another htag app, which will use the same component (MyText) for "hello" and "world". You can notice that, the second ("world") is set with a default background style (green). `kwargs` prefixed by `_` are automatically setted as attribut on the tag instance.

```python
from htag import Tag

class MyText(Tag.span):
    def init(self,txt, *a):
        self <= txt

class App(Tag.body):
    def init(self):
        self <= MyText("Hello")
        self <= MyText("World",_style="background:green")

if __name__=="__main__":
    from htag.runners import Runner
    Runner( App ).run()    # <= this is the runner
```

This will produce something like :

```html
<body id="140236411356880">
    <span id="140236411356544">Hello</span><span style="background:green" id="140236411356208">World</span>
</body>
```

`id`'s are just here, to keep coherence with python objects on python side.

If you want to set html attributs, at runtime (not in contructor phase), you simply set the dictitems of the Tag. Here is a version of the previous example using them.

```python
from htag import Tag

class MyText(Tag.span):
    def init(self,txt,color=None):
        self <= txt
        if color:
            self["style"]="background:%s" % color   # <- here is the trick

class App(Tag.body):
    def init(self):
        self <= MyText("Hello")
        self <= MyText("World","green")

if __name__=="__main__":
    from htag.runners import Runner
    Runner( App ).run()    # <= this is the runner

```

It will produce the same html rendering.

[More on Tag creations (the complete guide)](/htag/creating_a_tag/)

[The tutorial to create an "input" component](/htag/tuto_create_an_input_component/)


## Interactions

As you seen before, you can pass prefixed `kwargs` to define html attributs (or define them in the dictitems of the Tag), so this thing will work too :

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self <= Tag.button("Click me",_onclick="alert(42)")

if __name__=="__main__":
    from htag.runners import Runner
    Runner( App ).run()    # <= this is the runner
```

But, notice that the string which is setted in `_onclick` is just a javascript statement !

If you want to call "python side", you will need to use an another form, the simplest one :

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self <= Tag.button("Hello",_onclick=self.addContent)
        self <= Tag.button("World",_onclick=self.addContent)

    def addContent(self,object): # <= object is the instance of the htag instance which have called this method (here a Tag.button)
        self <= object.innerHTML

if __name__=="__main__":
    from htag.runners import Runner
    Runner( App ).run()    # <= this is the runner
```

When you will click the button, the instance of the object will add "some content" to itself (you can verify, by refreshing the page (f5))

!!! note "kind of methods"
    Here, the `addContent` method, is a **sync method**. But keep in mind, that it could be:

     * a **async method** (ex: `async def addContent(...)`)
     * a **sync generator** (ex: `def addContent(...): yield `)
     * or an **async generator** (ex: `async def addContent(...): yield `)

    The last two (the generator ones), let you use a `yield` statement, which will force current rendering to the client side, while processing the generator.

From here, you have seen 95% of the features of **htag**.

[More on interactions (the complete guide)](calling_an_event.md)


## Include ressources

**htag** provide a way to include some external ressources (think: css, js, favicon, ...). All theses ressources will be included in `<head>` tag, at construction time.
**htag** will scan the python Tag'classes and collect all of them to produce the heading parts of the html rendering.

The trick is to define a class attribut `statics`, to add your ressource ... a simple example :

```python
from htag import Tag

class App(Tag.body):
    statics = Tag.style("""body {background:yellow}""")

    def init(self):
        self <= "hello world"

if __name__=="__main__":
    from htag.runners import Runner
    Runner( App, port=9999).run()    # <= this is the runner
```

`statics` can be a Tag'instance or a list of Tag'instance.

!!! note "Discovering statics"
    By default, **htag** will discover all Tag'subclasses to include their statics, from the current process. But sometimes, it can be useful to include only thoses which we really need ; it's possible thru the class attribut `imports`, which should contain a list of Tag'class.


## Execute JS statements on client side

Sometimes, it can be useful to start a js statement ...

or make a js interaction with [@expose decorator](js_bidirectionnal.md)

**`** NEXT SOON **`**
