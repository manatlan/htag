# HTag : "[H]TML Tag"

The descendant of [gtag](https://github.com/manatlan/gtag) ... but :

 * Not tied to [guy](https://github.com/manatlan/guy)
 * Able to be used in anything which can display html/js/css (pywebview, cefpython3, a browser, .... or guy)
 * A **lot lot lot better and simpler** (better abstractions/code/concepts)
 * "intelligent rendering" (redraw only component on state changes)

It's a GUI toolkit for building GUI toolkits ;-)

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

## In French
Sorte de FWK (orienté composants), où on code (coté backend) des objets python (en fait des objets "Tag"), qui ont une representation HTML avec des interactions, qui peuvent s'executer dans tout ce qui est capable d'afficher du html/js/css (pywebview, cefpython3, a browser, ....)

Les "interactions" sont des actions émanants de la partie front vers le back, pour synchroniser l'état de l'objet (côté back), et retourner sa nouvelle représentation front.
La nature de ces interactions dépendent du `runner` utilisé (browser>ajax|websocket, guy>Websocket, pywebview>inproc)

Le fwk permet surtout de fabriquer ses composants ... et il faudrait utiliser ces composants dans une appli.

Autant le fwk permet des interactions avec js/front ... autant, il ne faudrait pas en faire dans les composants finaux : l'idée, c'est d'abstraire toutes interactions js : de manière à ce que ça soit totallement transparent dans les composants finaux.

