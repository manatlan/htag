# HTag : "H(tml)Tag"

<img src="https://manatlan.github.io/htag/htag.png" width="100" height="100">

[![Test](https://github.com/manatlan/htag/actions/workflows/on_commit_do_all_unittests.yml/badge.svg)](https://github.com/manatlan/htag/actions/workflows/on_commit_do_all_unittests.yml)

<a href="https://pypi.org/project/htag/">
    <img src="https://badge.fury.io/py/htag.svg?x" alt="Package version">
</a>


A new python library to create UI (or UI toolkit), which render nativly in anything which can render **html/js/css**.
Thoses can be a browser, a pywebview, an android/apk, or anything based on cef, depending on an [htag runner](https://manatlan.github.io/htag/runners/) !
As it's based on html/js rendering: you can easily mix powerful JS libs with powerful PY3 libs : and make powerful python apps !

 * For a **desktop app** : 
    * You can use the [PyWebView runner](https://manatlan.github.io/htag/runners/#pywebwiew), which will run the UI in a pywebview container 
    * You can use the [ChromeApp runner](https://manatlan.github.io/htag/runners/#chromeapp), which will run the UI in a local chrome in "app mode" (headless).
 * For a **android app** : You can use the [AndroidApp runner](https://manatlan.github.io/htag/runners/#androidapp), which will run the UI in a kiwi webview thru tornado webserver, and can be embedded in an apk ([recipes](https://github.com/manatlan/htagapk))
 * For a **pyscript app** : you can use the [PyScript runner](https://manatlan.github.io/htag/runners/#pyscript), which will run completly in client side
 * For a **web app** : You can use the [htagweb](https://github.com/manatlan/htagweb).

But yes … the promise is here : **it's a GUI toolkit for building "beautiful" applications for mobile, web, and desktop from a single codebase**.

[DOCUMENTATION](https://manatlan.github.io/htag/)

[DEMO/TUTORIAL](https://htag.glitch.me/)

[Changelog](https://github.com/manatlan/htag/releases)

[Available on pypi.org](https://pypi.org/project/htag/)

[Announcement on reddit (22/07/14)](https://www.reddit.com/r/Python/comments/vysnci/htag_a_new_gui_tookit_for_webdesktopandroid_from/)


Well tested:
 - Pytests on core at 99%
 - Real [Selenium TESTS in github CI/CD](https://github.com/manatlan/htag/actions/workflows/selenium.yaml)

## To have a look

 * [htag.glitch.me](https://htag.glitch.me/): A htag app, hosted on glitch.com, running with [htagweb](https://github.com/manatlan/htagweb). Many examples from simpler to complex ones, in tutorial spirit.
 * [pyscript/demo](https://raw.githack.com/manatlan/htag/main/examples/pyscript_demo.html): A htag app in a simple html page, running with [pyscript runner](https://manatlan.github.io/htag/runners/#pyscript). Many examples in a REPL mode (you can try/edit/run them). (ONLY HTML needed)

## ROADMAP to 1.0.0

 * the "0.60.x" is the pre-version before 1.0.0 (htag core will not change anymore). I need to fix some runners before.
 * tests tests
 * setup minimal docs, with [that](https://realpython.com/python-project-documentation-with-mkdocs/) ;-)
 * ~~top level api could change (Tag() -> create a Tag, Tag.mytag() -> create a TagBase ... can be a little bit ambiguous)~~
 * ~~manage "query params" from url to initialize Tags/routes~~
 * ~~I don't really like the current way to generate js in interaction : need to found something more solid.~~
 * ~~the current way to initiate the statics is odd (only on real (embedded) Tag's) : should find a better way (static like gtag ?!)~~

and more technicals :
- ~~better js try/catch to sort js/py error + try/catch on http com error (for thoses which kill session webhttp/pye) ~~
- ~~getStateImage is non sense coz it's str'ing (why not returning the str ?!)~~
- ~~mix the Tag.__init__ with the old system (like this: it's unmaintable)~~
- ~~introduce a virtual tag/placeholder~~
- DISPLAY a warning (or exception in STRICT_MODE), when a render method use a "tag creation" (ex: Tag.div("hello")), because it will always be rendered !!!!! -> bad habits

- ~~rename "tag" to "self" for js statements (keep the twos, for compatibility reasons)~~
- ~~Make it possibles -> NOT POSSIBLE currently ... abandonned ;-)~~
    ~~self.js = self.bind( self.starting , b'window.innerWidth') # doesn't work currently~~
    ~~self.js = self.bind.starting( b'window.innerWidth' ) # work (only reason to keep the "old form")~~

- ~~perhaps `self( js_statement)` -> `self.call( js_statement )` ... less confusing !~~
- ~~thus, to avoid `self( self.bind.method(*a,**k) )`, you can write `self.call.<method>( *a,**k )`~~



## History

At the beginning, there was [guy](https://github.com/manatlan/guy), which was/is the same concept as [python-eel](https://github.com/ChrisKnott/Eel), but more advanced.
One day, I've discovered [remi](https://github.com/rawpython/remi), and asked my self, if it could be done in a *guy way*. The POC was very good, so I released
a version of it, named [gtag](https://github.com/manatlan/gtag). It worked well despite some drawbacks, but was too difficult to maintain. So I decided to rewrite all
from scratch, while staying away from *guy* (to separate, *rendering* and *runners*)... and [htag](https://github.com/manatlan/htag) was born. The codebase is very short, concepts are better implemented, and it's very easy to maintain.


