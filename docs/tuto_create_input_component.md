# How to create your first "input" component

I assume that you have the base (see tutorial)

Let's create a minimal htag app :

```python
from htag import Tag

# the app side

class Test(Tag.body):
    def init(self):
        self <= "here, we want an input'able"

###############################################################################    
# the runner side
    
from htag.runners import DevApp

app=DevApp(Test)

if __name__=="__main__":
    app.run(port=10202)

```

Now, we want to create an input field. In the htag style, you will
create something like that (replace your `Test` class):
    
```python
class Test(Tag.body):
    def init(self):
        self <= Tag.input(_value="default" )        

```

Now, we've got an input field with a default value
Changing it, on UI side, does nothing.

Let's change that (replace your `Test` class):

```python
class Test(Tag.body):
    def init(self):
        self <= Tag.input(_value="default", _onchange = self.myonchange)
        
    def myonchange(self,o):
        print("it has changed")
```

Now, changing it on UI side notify the python side, that somethig has changed !
The callback `myonchange` receive the object which has fired the event (o).
But the input field has not sent its new content !

Let's change that (replace your `Test` class):

```python
class Test(Tag.body):
    def init(self):
        self <= Tag.input(_value="default", _onchange = self.bind( self.myonchange, b"this.value" ) )
        
    def myonchange(self,value:str):
        print("it has changed ->",value)
```

Assigning ` _onchange = self.myonchange` is strictly the same as `_onchange = self.bind( self.myonchange )`. 
But the form `self.bind( <method>, ....)` is better when you need to send arguments. In this case, it will send the client value
to the `myonchange` callback. Using the b"trick" to get data from client/js.

It's better, but it's a lot better to make it a "htag component", to be reusable in another app.

Let's create a `MyInput component`, and reuse it from the main class `Test` like that:

```python
class MyInput(Tag.input):
    def init(self,value=""):
        self.value = value  # store the real value in a property value
        self["value"]=self.value    # set the @value attrib of input
        self["onchange"] = self.bind( self._set, b"this.value" )

    def _set(self,value:str): # when change, keep the property value up-to-date
        self.value=value

class Test(Tag.body):
    def init(self):
        self <= MyInput("default")
        
```

Now, when you change the content of your `MyInput` ... the change is reflected on python side !

And you can rebind its onchange event, to get the changed value ....(replace your `Test` class)

```python
class Test(Tag.body):
    def init(self):
        self.myinput = MyInput("default")
        self.myinput["onchange"].bind( self.changed )
        
        self <= self.myinput
    
    def changed(self,o):
        print("Changed ->",o.value)             # o is the object which has fired the event
        print("Changed ->",self.myinput.value)  # or access direct to your reference
        
```

If you understand all that concepts ^^, you can start to build your own components.

Here is a login form, using our newly widget (replace your `Test` class):

```python
class Test(Tag.body):
    def init(self):
        self.mylogin = MyInput()
        self.mypass = MyInput()
        
        self <= Tag.div("Login:"+self.mylogin)
        self <= Tag.div("Passwd:"+self.mypass)
        self <= Tag.button("ok", _onclick=self.authent)
    
    def authent(self,o):
        if self.mylogin.value=="test" and self.mypass.value=="test":
            self.clear()
            self<= Tag.h1("You are in ;-)")
        else:
            self <= Tag.li("not the rights credentials ;-)")
        
```    
