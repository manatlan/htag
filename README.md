# HTag : "[H]TML Tag"

The descendant of [gtag](https://github.com/manatlan/gtag) ... but :

 * Not tied to [guy](https://github.com/manatlan/guy)
 * Able to be used in anything which can display html/js/css (pywebview, cefpython3, a browser, in [pyscript](https://pyscript.net/).... or [guy](https://github.com/manatlan/guy))
 * A **lot lot lot better and simpler** (better abstractions/code/concepts)
 * "intelligent rendering" (redraw only component on state changes)
 * and it runs in [pyscript](https://pyscript.net/) too ;-)

It's a GUI toolkit for building GUI toolkits ;-)

[DEMO/TUTORIAL](https://htag.glitch.me/)

[Changelog](changelog.md)

[Available on pypi.org](https://pypi.org/project/htag/)

**HTag** provides somes [`runners`](htag/runners) ootb. But they are just here, for the show. IRL: you should build your own, for your needs.

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
 * I don't really like the current way to generate js in interaction : need to found something more solid.
 * ~~the current way to initiate the statics is odd (only on real (embedded) Tag's) : should find a better way (static like gtag ?!)~~


