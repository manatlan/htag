# HTag

<img src="htag.png" width="100" height="100" style="float:right">

docs are coming ....

meanwhile, you can learn a lot on [htag's demo](https://htag.glitch.me/) ... or better [try/repl your self](https://raw.githack.com/manatlan/htag/main/examples/pyscript_demo.html)
(it's an htag app, running with the runner pyscript, in a simple html page, which provide examples in a html editor) ;-)


## Concept

The concept is simple : you create UI python classes, which inherits from `htag.Tag.<html_tag>` (which nativly render html/js/css, and provides minimal dom manipulation api). You can craft components, by reusing other components. Your main component is called the **htag app**.

And you run your **htag app**, with a [htag.runner](runners.md) ... (which will create an instance of it) ... And htag (the renderer part) will manage **interactions** between the client side and the python side. At each states change in python side, the rendering changes are done on client side. The 2 sides are keeped synchronous ! It only redraws components which has changed !

Of course, htag components can (or must) reuse htag components, and will enforce you to create them, to separate your UI logics... and build your own set of reusable components ! That's why htag is more taggued as an "UI Toolkit to build UI tookit", than an "UI toolkit to build GUI".

The (far from) perfect example is [htbulma](https://github.com/manatlan/htbulma), which is a set of "ready-to-use htag components", to build GUI from ground. It uses **htag**, and provide UI components, usable without (too many)knowledgement of html/js/css world.

**TODO**
