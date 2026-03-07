# HTag

<img src="htag.png" width="100" height="100" style="float:right">

... Docs are coming (2024/03/1) ... ;-)

Meanwhile, you can learn a lot on [htag's demo](https://htag.glitch.me/) ... or better [try/repl your self](https://raw.githack.com/manatlan/htag/main/examples/pyscript_demo.html)
(it's an htag app, running with the runner PyScript, in a simple html page, which provide examples in an html editor) ;-)


## Quick start

Just pip the **htag** lib, from [pypi.org](https://pypi.org/project/htag/)

```bash
$ pyhon3 -m pip install htag -U
```

Create a starter app ;-)

```bash
$ pyhon3 -m htag
```
(it will create a "main.py" basic htag app)

Start the app :

```bash
$ pyhon3 -m htag main.py
```

It will run the app, in a "basic UI" (open a tab in your default browser), in "developping mode" ("hot reload" while pressing F5/refresh, and htag errors popups in a nice message )

IRL, you should define your [Runner](runner.md) to not launch in "developping mode" ! Edit your "main.py" like that :

```python
...
if __name__=="__main__":
    Runner(App,interface=(640,480)).run()
```

And run it like that :

```bash
$ pyhon3 main.py
```

Note :

 - REAL MODE, no "developping mode", pressing F5 will not recreate instances (the app), and "errors" will be ignored silently in UI.
 - here, it will run the "UI part" in a "chrome app mode" (healess chrome) (you'll need to have chrome installed, but it will fallback to a normal tab in default browser if not.
 - The [Runner](runner.md) got a lot of options ;-)
 - There are more [Runners](runners.md). But :

    - if you want to make a "web app" (for many users) you should use [htagweb](https://github.com/manatlan/htagweb)
    - if you want to make an Android (smarthpone/TV) app, you should use [htagapk](https://github.com/manatlan/htagapk)


Now, you can continue on [tutorial](tutorial.md) ;-)

## Concept

You can see it like a python way to create apps, which can use the best of python world, and the best of html/javascript world. And best of all, you can **easily** create apps (same codebase!) that will work in desktop, android & web world (& html only too (thansk to [PyScript](https://manatlan.github.io/htag/runners/#pyscript) )) .

The concept is simple : you create UI python classes, which inherits from `htag.Tag.<html_tag>` (which nativly render html/js/css, and provides minimal dom manipulation api). You can craft components, by reusing other components. Your main component is called the **htag app**.

And you run your **htag app**, with a [htag.runner](runners.md) ... (which will create an instance of it) ... And htag (the renderer part) will manage **interactions** between the client side and the python side. At each states change in python side, the rendering changes are done on client side. The 2 sides are keeped synchronous ! It only redraws components which has changed !

Of course, htag components can (or must) reuse htag components, and will enforce you to create them, to separate your UI logics... and build your own set of reusable components ! That's why htag is more taggued as an "UI Toolkit to build UI tookit", than an "UI toolkit to build GUI".

The (far from) perfect example is [htbulma](https://github.com/manatlan/htbulma), which is a set of "ready-to-use htag components", to build GUI from ground. It uses **htag**, and provide UI components, usable without (too many)knowledgement of html/js/css world.


