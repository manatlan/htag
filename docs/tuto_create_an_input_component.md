# How to create your first "input" component

I assume that you have the minimal bases (html's crafting and events bindings). And I will show you how to create an "reactive" input field .... it's, by far, the most complex thing ;-). But it's a component which cover well all the core features of htag concepts. If you understand that : you can start to craft your own/complex components easily.

Let's create a minimal htag app, which is runn'able as is (if you got the dependencies for the DevApp runner):

```python
from htag import Tag

###############################################################################    
# the app side
###############################################################################    
class Test(Tag.body):
    def init(self):
        self <= "here, we want an input'able"

###############################################################################    
# the runner side
###############################################################################    
if __name__=="__main__":
    from htag.runners import Runner
    Runner(Test).run()

```

Now, we want to create an input field. In the htag style, you will
create something like that (replace your `Test` class):
    
```python
class Test(Tag.body):
    def init(self):
        self <= Tag.input(_value="default" )        

```

Now, we've got an input field with a default value.
Changing it, on UI side, does nothing.

Let's change that (replace your `Test` class):

```python
class Test(Tag.body):
    def init(self):
        self <= Tag.input(_value="default", _onchange = self.myonchange)
        
    def myonchange(self,o):
        print("it has changed")
```

Now, changing it on UI side notify the python side, that something has changed !
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
to the `myonchange` callback (using the `b"trick"` to get data from client/js side).

It's better, but it will be a lot better to make it a **"htag component", to be re-usable in another htag apps**.

Let's create a `MyInput component`, and reuse it from the main class `Test` like that:

```python
class MyInput(Tag.input):
    def init(self,value=""):
        self.value = value  # store the real value in a property value
        self["value"]=self.value    # set the @value attrib of html'input
        self["onchange"] = self.bind( self._set, b"this.value" )    # assign an event to reflect change

    def _set(self,value:str): # when changed, keep the property value up-to-date
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
        
        #construct the layout
        self <= self.myinput
    
    def changed(self,o):
        print("Changed ->",o.value)             # o is the object which has fired the event
        print("Changed ->",self.myinput.value)  # or access direct to your reference
        
```

If you understand all that concepts ^^, you can start to build your own/complex components.

Here is a login form, using our newly widget (replace your `Test` class):

```python
class Test(Tag.body):
    def init(self):
        self.mylogin = MyInput()
        self.mypass = MyInput()
        
        #construct the layout
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
**To go further**

You will notice that when you input bad credentials, the form is resetted to its initial values ! It's normal, because the `authent` method will modify the `Test` component's content (adding a `Tag.li` to `self`), which had the effect to force the redraw of the `Test` component on UI side !

If you want to avoid this behaviour, simply add the `Tag.li` in another part of the UI (or simply remove the last 2 lines), like that :

```python
class Test(Tag.body):
    def init(self):
        self.mylogin = MyInput()
        self.mypass = MyInput()
        self.result = Tag.div()
        
        #construct the layout
        self <= Tag.div("Login: "+self.mylogin)
        self <= Tag.div("Passwd: "+self.mypass)
        self <= Tag.button("ok", _onclick=self.authent)
        self <= self.result
    
    def authent(self,o):
        if self.mylogin.value=="test" and self.mypass.value=="test":
            self.clear()
            self<= Tag.h1("You are in ;-)")
        else:
            self.result <= Tag.li("not the rights credentials ;-)")
```

Because only `self.result` (Tag.div) is modified ... only `self.result` will be redraw on UI side.

Now, you should really understand 95% of the core htag features




