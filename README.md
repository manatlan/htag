# THAG : "[T]he [H]TML [A]ttributs [G]UI"

The descendant of [gtag](https://github.com/manatlan/gtag) ... but :

 * Not tied to [guy](https://github.com/manatlan/guy)
 * Able to be used in anything which can display html/js/css (pywebview, cefpython3, a browser, ....)
 * A lot lot lot better and simpler (better abstractions/code/concepts)
 * "intelligent rendering" (redraw only component with states changes)

It's a GUI toolkit for building GUI toolkits ;-)

[Changelog](changelog.md)

**Thag** provides somes [`runners`](thag/runners) ootb. But they are here just for the show. IRL, you should build your own, for your needs.

## In French
Sorte de FWK (orienté composants), où on code (coté backend) des objets python (en fait des objets "Tag"), qui ont une representation HTML avec des interactions, qui peuvent s'executer dans tout ce qui est capable d'afficher du html/js/css (pywebview, cefpython3, a browser, ....)

Les "interactions" sont des actions émanants de la partie front vers le back, pour synchroniser l'état de l'objet (côté back), et retourner sa nouvelle représentation front.
La nature de ces interactions dépendent du `runner` utilisé (browser>ajax|websocket, guy>Websocket, pywebview>inproc)

Le fwk permet surtout de fabriquer ses composants ... et il faudrait utiliser ces composants dans une appli.

Autant le fwk permet des interactions avec js/front ... autant, il ne faudrait pas en faire dans les composants finaux : l'idée, c'est d'abstraire toutes interactions js : de manière à ce que ça soit totallement transparent dans les composants finaux.

