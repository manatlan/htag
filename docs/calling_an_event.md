# Calling an event : the complete guide ;-)

## The simple way ...

```python
from htag import Tag

class App(Tag.body):
    def init(self):
        self += Tag.button("click", _onclick=self.clicked)

    def clicked(self, object_which_has_emitted_the_event):
        print( object_which_has_emitted_the_event )
```

The "_onclick" parameter decalres the callback on the "onclick" event of the button.
When you click the button, htag will emit an "interaction" between the GUI/client_side and the back/serverside/your_python_code.
The first, and only argument, is the instance of the object which has emitted the event.

This kind of interaction is called "direct" : the callback is directly called during the interaction.

For your interest ... it exactly the same construction as
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

It's not really a good practice, when you need to transfer _python values_ ... Prefer the previous method !

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
...

