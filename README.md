# HTag : "H(tml)Tag"

<img src="docs/htag.png" width="100" height="100">

[![Test](https://github.com/manatlan/htag/actions/workflows/unittests.yml/badge.svg)](https://github.com/manatlan/htag/actions/workflows/unittests.yml)

A new python library to create UI (or UI toolkit), which can be rendered in anything which can render **html/js/css**.
Thoses can be a browser, a pywebview, an android/apk, or anything based on cef, depending on an [htag runner](https://manatlan.github.io/htag/runners/) !

 * For a **desktop app** : You can use the [PyWebView runner](https://manatlan.github.io/htag/runners/#pywebwiew), which will run the UI in a pywebview container (or "ChromeApp runner", in a local chrome app mode). 
 * For a **web app** : You can use the [WebHTTP runner](https://manatlan.github.io/htag/runners/#webhttp), which will run the UI in a web server, and serve the UI on client side, in a browser. 
 * For a **android app** : You can use the [AndroidApp runner](https://manatlan.github.io/htag/runners/#androidapp), which will run the UI in a kiwi webview thru tornado webserver, and can be embedded in an apk ([recipes](https://github.com/manatlan/htagapk))
 * For a **pyscript app** : you can use the [PyScript runner](https://manatlan.github.io/htag/runners/#pyscript), which will run completly in client side

But yes … the promise is here : **it's a GUI toolkit for building "beautiful" applications for mobile, web, and desktop from a single codebase**.

[DOCUMENTATION](https://manatlan.github.io/htag/)

[DEMO/TUTORIAL](https://htag.glitch.me/)

[Changelog](https://github.com/manatlan/htag/blob/main/changelog.md)

[Available on pypi.org](https://pypi.org/project/htag/)



## To have a look

See the [demo source code](https://github.com/manatlan/htag/blob/main/examples/demo.py)

To try it :

    $ pip3 install htag pywebview
    $ wget https://raw.githubusercontent.com/manatlan/htag/main/examples/demo.py
    $ python3 demo.py


## ROADMAP to 1.0.0

 * rock solid (need more tests)
 * setup minimal docs ;-)
 * ~~top level api could change (Tag() -> create a Tag, Tag.mytag() -> create a TagBase ... can be a little bit ambiguous)~~
 * add a runner with WS with stdlib ? (not starlette!)
 * ~~I don't really like the current way to generate js in interaction : need to found something more solid.~~
 * ~~the current way to initiate the statics is odd (only on real (embedded) Tag's) : should find a better way (static like gtag ?!)~~


## History

At the beginning, there was [guy](https://github.com/manatlan/guy), which was/is the same concept as [python-eel](https://github.com/ChrisKnott/Eel), but more advanced.
One day, I've discovered [remi](https://github.com/rawpython/remi), and asked my self, if it could be done in a *guy way*. The POC was very good, so I released
a version of it, named [gtag](https://github.com/manatlan/gtag). It worked well despite some drawbacks, but was too difficult to maintain. So I decided to rewrite all
from scratch, while staying away from *guy* (to separate, *rendering* and *runners*)... and [htag](https://github.com/manatlan/htag) was born. The codebase is very short, concepts are better implemented, and it's very easy to maintain.


