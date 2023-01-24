# Calling an event : the complete guide ;-)

After months of use, and more than 100 htag apps later, here are my notes ;-)

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
The first, and only argument, is the instance of the object which has emitted the event.

This kind of interaction is called "direct" : the callback is directly called during the interaction.

!!! note "For your interest ... it exactly the same construction as"
    ```python
        def init(self):
            button=Tag.button("click")
            button["onclick"]=button.bind( self.clicked ) # declare event, post button construction
            self += button
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

using the _b'trick_, to ask **htag** to get a javascript statement.

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

## The old way

There is another way to do things, it's historical, it comes from the old gtag. But sometimes it's usefull too. I hesitate to talk here, because it's clearly deprecated. And should be avoided ... but sometimes, it's handsfull !

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
The `self.bind.<method>(*args,**kargs)` return a string (a javascript statement to do an interaction).
The 'method' must be declared on self instance. It's a lot simpler, but a lot less powerful.

By opposite, the `<instance>.bind( <method>, *args, **kargs)` return a Caller Object, which is rendered as a string (javascript statement). This second form is more versatile, because you can bind any python/callback method. And build better abstractions/components. **But sometimes, you'll need to bind a real binded method ... which is not possible in some cases with this second form (during construction phases)** (TODO: need to developp here)

You should prefer/use this second form. Because the `self.bind.<method>(*args,**kargs)` is deprecated, and could disappear one day.
In all cases, this old form will be in htag 1.0.0 !

## The Caller object

The Caller object (returned by the form `<instance>.bind( <method>, *args, **kargs)`) is v(ery) usefull. Because, you can chain events, and you can add customized javascript calls.

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


# Others ways

Each htag's Tag got a 'js' property. This js property can contain javascript to be executed at each Tag rendering.

Here is a very classical use :
```python
class App(Tag.div):
    def init(self):
        self+=Tag.input(_value="default", js="tag.focus()")
```

So, every time the Tag 'App' is rendered, it creates an input field, and take the focus (`tag` is a special js var, in this context, to quickly access to the input element) (BTW : it should be named 'self' to be more consistent, perhaps in a post 1.0.0 version).

Another approach could be :

```python
class App(Tag.div):
    def init(self):
        self+=Tag.input(_value="default" )
        self.js = "tag.childNodes[0].focus()"
```
In this case, it's the App Tag which use its js property to set the focus on its child (in a js way)

So, this js property can send back data from client_side/gui too.

Here is an example :
```
class App(Tag.body):
    def init(self):
        # self.js = self.bind( self.starting , b'window.innerWidth') # doesn't work currently
        self.js = self.bind.starting( b'window.innerWidth' )
        
    def starting(self,width):
        print("innerWidth",width)
...
Currently, only the "old form" works ;-( ... the newest `self.bind( <method>, *args, **kargs)` can't, But will try to fix that before 1.0.0. And it's the only main reason why the old form is still there ;-(


