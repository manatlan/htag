# HRenderer

It's the class which handle an htag.Tag class, and make it lives in a runner context. It exposes methods for a [runner](runners.md).

In general, you don't need to use this class on your own. In general, you will use a 'runner' which will do it for you. If you are
here, you will to create your own runner, or see how it works.

definitions:

 * hr : means the HRrenderer instance
 * runner : it's a high level class (which use a hrenderer under-the-hood) to make the magix.


## `def __init__(self, tagClass: type, js:str, exit_callback:Optional[Callable]=None, init= ((),{}), fullerror=False, statics=[], session=None ):`

It's the constructor of an instance ;-)

When you got your hr instance : `str(hr)` will (always) contain a full html page which should work OOTB in a client-side ! It's often
called the "1st rendering".

### tagClass [htag.Tag class] 
It's the subclass, which will be instanciate in the hr instance. 

### js [str]
It's a string which define the JS methods to interact with the hr instance, and the way to "start" the live
of the html page in client side (by calling a js 'start()' method).

For a http runner, it's often like that:
```python
async function interact( o ) {
    action( await (await window.fetch("/",{method:"POST", body:JSON.stringify(o)})).text() )
}

window.addEventListener('DOMContentLoaded', start );
```

For a websocket runner, it's often like that:

```python
async function interact( o ) {
    ws.send( JSON.stringify(o) );
}
var ws = new WebSocket("ws://"+document.location.host+"/ws");
ws.onopen = start;
ws.onmessage = function(e) {
    action( e.data );
};
```

There are 3 main ideas, in this js str :

 * provide a js 'interact' method, which will pass its arguments, to python (back side)
 * provide the way to call the `action( <dict> )` from the python response (back side)
 * define how to call the 'start()' method

Remarks
 - start() and action( <dict> ) are js methods provided by the "1st rendering"
 - as you can see :
     - The http form is synchronous (the action is executed with the return of the interact)
     - The ws form is asynchronous (the action is executed when a message is sended from the hr to the client side)


### init [tuple<tuple,dict>]
it's the parameters which will be used to initialize the htag.Tag class, in the form (*args, **kargs).

If it can't instanciate the class with the init parameters, it will try to instanciate it with null parameters ( aka `( (), {} )`).

### fullerror [boolean]
it's a boolean to prevent the hr to send back just the error, or the full stacktrace. 

### statics [List<str|htag.Tag>]
It's a list of "statics", which will be added in the html>head page of the 1st rendering.

### session [dict]
It's a dict which will hold the session for the user. It got only sense in the "web runners" (those ones manage a session/dict by user). All others runners are mono-user,
so the session dict will only be a empty dict.

### exit_callback [method]
It's a method, which will be called when a user call the tag.exit() method. It got only sense in runners which are mono-user (because it will quit the app). The "web runners"
dont implement this feature.


## `async def interact(self, id, method_name:str, args, kargs, event=None) -> dict:`

It's the python method, which must be called thru the 'js' declaration in the hr constructor, to make an "interaction"
with the tag instance, managed by the hr.

In general, you won't need to pass arguments to it because : you just cable the js call

Under the hood, this method returns 'actions' (dict), to redraw the client side, and to execute some js.
...


**TODO** I find it ambiguous ... because the reality is simpler !

