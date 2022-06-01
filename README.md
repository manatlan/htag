# HTag : "[H]TML Tag"

A new python library to create UI (or UI toolkit), which can be rendered in anything which can render **html/js/css**.
Thoses can be a browser, a pywebview, or anything based on cef, depending on an "htag runner" (`*`) !

 * For a **desktop app** : You can use the "PyWebView runner", which will run the UI in a pywebview container (or "ChromeApp runner", in a local chrome app mode). 
 * For a **web app** : You can use the "WebHTTP runner", which will run the UI in a web server, and serve the UI on client side, in a browser. 
 * For a **android app** : You can use the "Guy runner", which will run the UI in a kiwi webview, and can be embedded in an apk (`**`)
 * For a **pyscript app** : you can use the "PyScript runner", which will run completly in client side

But yes … the promise is here : it's a GUI toolkit for building "beautiful" applications for mobile, web, and desktop from a single codebase.

(`*`) **HTag** provides somes [`runners`](htag/runners) ootb. But they are just here for the show. IRL: you should build your own, for your needs.

(`**`) **HTag** is not tied to [guy](https://github.com/manatlan/guy), but can use it as is. So, a **HTag app** could be packaged in an apk/android, using [a guy method](https://manatlan.github.io/guy/howto_build_apk_android/). But in the future, **HTag** will come with its own "android runner" (without *guy* !)


[DEMO/TUTORIAL](https://htag.glitch.me/)

[Changelog](changelog.md)

[Available on pypi.org](https://pypi.org/project/htag/)



## To have a look

See the [demo source code](https://github.com/manatlan/htag/blob/main/examples/demo.py)

To try it :

    $ pip3 install htag pywebview
    $ wget https://raw.githubusercontent.com/manatlan/htag/main/examples/demo.py
    $ python3 demo.py

There will be docs in the future ;-)

## ROADMAP to 1.0.0

 * rock solid (need more tests)
 * ~~top level api could change (Tag() -> create a Tag, Tag.mytag() -> create a TagBase ... can be a little bit ambiguous)~~
 * add a runner with WS with stdlib ? (not starlette!)
 * ~~I don't really like the current way to generate js in interaction : need to found something more solid.~~
 * ~~the current way to initiate the statics is odd (only on real (embedded) Tag's) : should find a better way (static like gtag ?!)~~


## History

At the beginning, there was [guy](https://github.com/manatlan/guy), which was/is the same concept as [python-eel](https://github.com/ChrisKnott/Eel), but more advanced.
One day, I've discovered [remi](https://github.com/rawpython/remi), and asked my self, if it could be done in a *guy way*. The POC was very good, so I released
a version of it, named [gtag](https://github.com/manatlan/gtag). It worked well despite some drawbacks, but was too difficult to maintain. So I decided to rewrite all
from scratch, while staying away from *guy* (to separate, *rendering* and *runners*)... and [htag](https://github.com/manatlan/htag) was born. The codebase is very short, concepts are better implemented, and it's very easy to maintain.


