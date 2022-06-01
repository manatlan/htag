# Tutorial

## Construction

`htag.Tag` is the basic object, and the only one you'll need to use, to build an htag app. The simplest htag app could be :

```python
from htag import Tag

class App(Tag.body): #<= define the html tag container of the app
    """ This is the most simple htag component """

    def init(self):
        # I'm just a div, with a textual node content "hello world"
        self <= "Hello world"   # shortcut for self.add("Hello world")

if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP( App ).run()    # <= this is the runner

```

As you can notice, it use the simplest constructor `init()`, to construct itself (best practice). But could be replaced by the real form too:

```python
    def __init__(self, **kwargs):
        # I'm just a div, with a textual node content "hello world"
        super().__init__(**kwargs)
        self <= "Hello world"   # shortcut for self.add("Hello world")
```

The simplest form avoid you to deal with the real construction phase under the hood. Because `kwargs` are used to define html attributs (or instance properties) from the ground.

Here is another htag app, which will use the same component (MyText) for "hello" and "world". You can notice that, the second ("world") is set with a default background style (green). `kwargs` prefixed by `_` are automatically setted as attribut on the tag instance.

```python
from htag import Tag

class MyText(Tag.span):
    def init(self,txt):
        self <= txt

class App(Tag.body):
    def init(self):
        self <= MyText("Hello")
        self <= MyText("World",_style="background:green")

if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP( App ).run()    # <= this is the runner
```

This will produce something like :

```html
<body id="140236411356880">
    <span id="140236411356544">Hello</span><span style="background:green" id="140236411356208">World</span>
</body>
```

`id`'s are just here, to keep coherence with python objects on python side.

## Interactions

As you seen before, you can pass prefixed `kwargs` to define html attributs, so this thing will work too :

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self <= Tag.button("Click me",_onclick="alert(42)")

if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP( App ).run()    # <= this is the runner
```

But, notice that the string which is setted in `_onclick` is just a javascript statement !

If you want to call "python side", you will need to use an another form, the simplest one :

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self <= Tag.button("Click me",_onclick=self.addContent)

    def addContent(self,object): # <= object is the instance of the htag instance which have called this method
        self <= "some content"

if __name__=="__main__":
    from htag.runners import BrowserHTTP
    BrowserHTTP( App ).run()    # <= this is the runner
```

When you will click the button, the instance of the object will add itself "some content" (you can verify, by refreshing the page (f5))

From here, you have seen 90% of the features of **htag**.

**`** NEXT SOON **`**