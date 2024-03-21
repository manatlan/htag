# Calling an event : the complete guide ;-)

After months of use, and more than 100 htag apps later, here are my notes ;-)

**TODO**: talk about the "ev" mechanism introduced in "htag 0.100.x"

## First of all

You should really understand than setting an onclick event, is just a javascript call. So this thing will work as expected, on client side :

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self+=Tag.button("click",_onclick="alert(42)")
```
It will call a javascript statement `alert(42)`, which will display a js alert box. It's the base.
But it's not a htag interaction ... just a js interaction.

## The simple way ...

to call an htag interaction ... could be:

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=self.clicked)

    def clicked(self, object_which_has_emitted_the_event):
        print( object_which_has_emitted_the_event )
```

The `_onclick` parameter declares the callback on the "onclick" event of the button.
When you click the button, htag will emit an "interaction" between the GUI/client_side and the back/serverside/your_python_code.
In the callback : the first, and only argument, is the instance of the object which has emitted the event.

This kind of interaction is called "direct" : the callback is directly called during the interaction.

!!! note "For your interest ... it exactly the same construction as"
    ```python
        def init(self):
            button=Tag.button("click")
            button["onclick"]=button.bind( self.clicked ) # declare event, post button construction
            self += button
    ```
    The method `<instance>.bind( method, **args, **kargs )` is the natural way to bind an "event", in all cases.

BTW, I think it's a good practice to not poluate the inner namespaces of the instance, by declaring methods which has only one client. Here we could do:
(as is, you keep your code more consistant, and less confusing)
```python
from htag import Tag

class App(Tag.body):
    def init(self):

        def clicked(object_which_has_emitted_the_event):
            print( object_which_has_emitted_the_event )

        self += Tag.button("click", _onclick=clicked)
```

## Pass arguments (in 'direct' calls)

If you want to pass arguments : a really good practice is to set them on the instance of the object, and get back in the callback.

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self += Tag.button("click A", my_arg="A", _onclick=self.clicked)
        self += Tag.button("click B", my_arg="B", _onclick=self.clicked)

    def clicked(self, object_which_has_emitted_the_event):
        print( object_which_has_emitted_the_event.my_arg )
```

It's a really good practice to adopt this kind of technics, for 95% of your events, and you keep your code simple and conscise.

## Pass arguments, using the "bind" (in 'direct' calls)

As seen before, the method `<instance>.bind( method, **args, **kargs )` can make a lot for you.

You could do :

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        button1=Tag.button("click")
        button1["onclick"]=button1.bind( self.clicked, "A" )
        self += button1

        button2=Tag.button("click")
        button2["onclick"]=button2.bind( self.clicked, "B" )
        self += button2

    def clicked(self, object_which_has_emitted_the_event, my_arg):
        print( my_arg )
```
Here, the argument is passed during the interaction, to the callback.

It's not really a good practice, when you need to transfer _python values_ ... Prefer the previous method (It's more readable, and avoid to have bigger interactions) !

This kind of form is needed when you want to send back _javascript values_

Example : if you want to get back an input value in real time

using the _b'trick_, to ask **htag** to get a javascript statement. This trick let you declare statements (as byte string) which will be interpreted as a "javascript statement". It's really handy to interact easily, in bind methods only.

```python
class App(Tag.body):
    def init(self):
        input=Tag.input(_value="")
        input["onkeyup"]=input.bind( self.changed, b"this.value" )
        self += input

    def changed(self, object_which_has_emitted_the_event, own_value):
        print( own_value )
```
It's the "only way" (not really ... but the proper way, for sure), to get back a information from the client_side/javascript.

Another regular use of this form is :

```python
class App(Tag.body):
    def init(self):
        self+=Tag.input(_value="",_onkeyup=self.bind( self.changed, b"this.value" ))

    def changed(self, own_value):
        print( own_value )
```

note that the event onkeyup is binded on the self (not on the button as previously), so the object which send the event is 'self' ... and thus, the self is the object_which_has_emitted_the_event.

This kind of approach is more component oriented, when you want to make beautiful component.

## passing arguments (in "undirect calls"))

Another regular approach, is to create a callback on the event : so the callback is called after the interaction.

But in all theses "undirect calls" : you can't get back values from client_side/javascript ...

``` python
class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=lambda object_which_has_emitted_the_event: self.clicked("A"))
        self += Tag.button("click", _onclick=lambda object_which_has_emitted_the_event: self.clicked("B"))

    def clicked(self, my_val):
        print( my_val )
```

or better (setting arguments in instance itself:

```python
class App(Tag.body):
    def init(self):
        for i in "ABCDEF":
            self += Tag.button(i, value=i, _onclick=lambda object_which_has_emitted_the_event: self.clicked( object_which_has_emitted_the_event.value ))

    def clicked(self, my_val):
        print( my_val )

```

## The old/historic way

There is another way to do things, it's historical, it comes from the old gtag. But sometimes it's usefull too.

In gtag, the way to bind an event was .... here in htag :

```python
class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=self.bind.clicked() )

    def clicked(self):
        print( "hello" )
```

and if you want to pass "python parameters" :

```python
class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=self.bind.clicked('hello') )

    def clicked(self, txt):
        print( txt )
```

and if you want to pass "javascript parameters" (using the `b'trick`)

```python
class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=self.bind.clicked(b'window.innerWidth') )

    def clicked(self, txt):
        print( txt )
```
The `<instance>.bind.<method>(*args,**kargs)` return a string (a javascript statement to do an interaction).
The 'method' must be declared on self instance. It's a lot simpler, but a lot less powerful.

By opposite, the `<instance>.bind( <method>, *args, **kargs)` return a Caller Object, which is rendered as a string (javascript statement). This second form is more versatile, because you can bind any python/callback method. And build better abstractions/components. **But sometimes, you'll need to bind a real binded method ... which is not possible in some cases with this second form (during construction phases)**

**BE AWARE** : if you are in a construction phase (`init(self)` or `__init__(self)`). New mechanisms (`<instance>.bind( <method>, *args, **kargs)`) can't work, because, at this time, in many cases, we don't know the parent/root of the instance ;-()

In that cases, the `<instance>.bind.<method>(*args,**kargs)` give better results.

## The Caller object

The Caller object (returned by the form `<instance>.bind( <method>, *args, **kargs)`) is (very) usefull. Because, you can chain events, and you can add customized javascript calls.

Here is an example of an interaction AND a post javascript statement.

```python
class App(Tag.body):
    def init(self):
        self+=Tag.button("right click",_oncontextmenu=self.bind( self.clicked )+"return false")

    def clicked(self):
        print( "right clicked" )
```
If you right click on the button, it will produce an htag interaction, and will stop the event (prevent to display the real/default contextmenu). In 99% of my cases, I use this, for my "oncontextmenu" events


Here is an example of chaining events.

```python
class App(Tag.body):
    def init(self):
        self+=Tag.button("click",_onclick=self.bind( self.clicked ).bind( self.clicked2))

    def clicked(self):
        print( "clicked" )
    def clicked2(self):
        print( "clicked2" )
```
It's very rare to use this feature. But can be usefull in complex components, to chain others treatments. BTW, it produces only one htag interaction (by opposite of the old form, where you could do the same, like `_onclick=self.bind.clicked()+";"+self.bind.clicked2()` ... but avoid that, it makes 2 htag interactions !)

And of course, you can mix them


## Others ways (using `Tag.js` property)

Each htag's Tag instance got a 'js' property. This js property can contain javascript to be executed at each Tag rendering.

Here is a very classical use :
```python
class App(Tag.div):
    def init(self):
        self+=Tag.input(_value="default", js="self.focus()") # here the .js is for the input.
```

So, every time the Tag 'App' is rendered, it creates an input field, and take the focus (`self` is a special js var, in this context, to quickly access to the input element)

**For versions <= 0.9.13** : the `self` was named `tag` (which worked too). You could use both, to refer to the js/nodeElement of the tag, but prefer to use `self` ;-)
**For versions <= 0.13.0** : the `self`, and `tag` was accepted
**For versions > 0.20.0** : only `self` ;-)


Another approach could be :

```python
class App(Tag.div):
    def init(self):
        self+=Tag.input(_value="default" )
        self.js = "self.childNodes[0].focus()"
```
In this case, it's the App Tag which use its js property to set the focus on its child (in a js way) (`self` is a special js var, in this context, to quickly access to the App/Tag.div js/nodeElement)

So, this js property can send back data from client_side/gui too.

Here is an example :

```python
class App(Tag.body):
    def init(self):
        self.js = self.bind.starting( b'window.innerWidth' )

    def starting(self,width):
        print("innerWidth",width)
```
As seen before, the newest `<instance>.bind( <method>, *args, **kargs)` couldn't be used for this purpose. Keep in mind, that this form should be used in binding events (because it needs to be "attached" in the dom tree)

## Others ways (using `Tag.call` method)

Each htag's Tag instance got a a `<instance>.call(js)` method to send an UNIQUE custom js statements during an interaction.

It's a little weird here. But it's really important to understand the difference between `self.js="js_statement()"` and `self.call("js_statement()")`.

 * `self.js="js_statement()" `: will execute the JS at each rendering of the object (ex: some html object (those from [materialize](https://materializecss.com/) need to be initialized with javascript statements, it's the perfect way to do that, in that place)
 * `self.call("js_statement()")` : will execute the JS one time (when it's called) (ex: some html object need to change its aspect thru js call ... think : close a menu, etc ...)

So, this thing will work as the previous one .. except ..

```python
class App(Tag.body):
    def init(self):
        self.call( self.bind.starting( b'window.innerWidth' ) )

    def starting(self,width):
        print("innerWidth",width)
```
Except ... here, the js is sent only at construction time (in previous one : the js is sent at each rendering).
The nuance is really subtil.

BTW, you can use a simple form (versions >= 0.9.14), which does exactly the same thing ^^:
```python
class App(Tag.body):
    def init(self):
        self.call.starting( b'window.innerWidth' )

    def starting(self,width):
        print("innerWidth",width)
```
Here : `self.call.starting( b'window.innerWidth' )` is the short form for `self.call( self.bind.starting( b'window.innerWidth' ) )`, it's exactly the same !

**IMPORTANT** :
The last 2 examples are BAD PRACTICE, because the `self.call` (during construction phase) can only work when it's in the main tag (which is managed by the Runner (TODO:link)). If it was in an `init` from a component : it can't work (because we don't know the parent/root at this time). The good practice is DON'T USE `self.call` IN A CONSTRUCTOR (prefer `self.js`)

## Using the `event` properties from gui/js

Some times, it can be usefull to get back the properties of the js event, when you want to get back the key pressed, or the x/y coordinates of a click, etc ...

Theses properties are stocked in the "event" property of an HTag instance, as a dict (during an interaction).

You can display them, like that:

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=self.clicked)

    def clicked(self, o):
        print( o.event )
```

## Using the `@expose` decorator 
See [@expose](js_bidirectionnal.md) !

...TODO...
