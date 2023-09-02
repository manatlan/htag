# RunnersBronx

This term "Bronx" is just here to define the current troubles with "all runners". And I would like to clarify all, before releasing the long awaited "1.0" ;-)

And it bothers me ... because I can't find the way to follow ;-)

This page is just here, for me, to try to expose troubles ;-)
(it's a lot of notes)

## update 2023/9/2
last thoughts ;-)

Module "htag", could:
- provides basic runners (but no web ones) ... only mono user
- remove webhttp/webws .. (move them in htagweb ?!)

Module "htagweb", could:
- be the official way to serve htag'apps on the web
- but require py3.8 (coz "[shared memory dict](https://github.com/manatlan/shared-memory-dict-py37)" (needed for multiple workers)) ... which is not possible on rpi/glitch (py3.7!) ;-(
- no WS on glitch ;-( ... so should provide at least an web/http one


## update 2023/9/1

Futur is brighter ;-)

But no decision at this time ...  But on web/server side, for multiple users ... I will certainly stick on htagweb.AppServer, which is the best of two worlds (others could web runners could disapper). It could be a lot simpler (for a lot of reasons (technically, maintenance, use cases, ...))

On web side, could persist htagweb.AppServer & htagweb.HtagServer (which could reuse htagweb.AppServer ?!). All others would be removed (WebHTTP & co)

On client side : (ChromeApp, BrowserHTTP, DevApp, AndroidApp ...) could stay as is

The only down-side : explain that a same app could not work as-is on both sides. (on client side, instances are lives ... on web side : instances are destroyed/recreated at each F5, and states should be in `self.root.states` (perhaps there is a solution, to make it transparent on each sides ?!)
...


## Prob#1 the bronx ?
There are several troubles:

 1) continue to provide embbeded runners with htag module ? (or make them in separate libs (like htagweb for web))
 2) Signatures differs (a bit) from a runner to another one
 3) spezialize the way it should work. Because some can use more features than others (hr and hr2 ?!?)
 4) and ensure current compatibilities, or breaks all before 1.0 ?!

The current core works well ... and the HRenderer (which is not perfect) is great.

But managing all theses runners is a big pain, to make them compatible between them. And sometimes, it's not possible at all (tag.update feature). I feel that I need to resolve this "bronx", before a "1.0" ;-)

The new "htagweb.HtagServer" is *really* top (all htag/web features, easy to maintain, robust) ... and could be better, as a simple middleware to manage htag lifespan, in a classical starlette/fastapi/django app (which could be a game changer).
But it got some severe limitations, compared to its web brothers (htagweb.WebServer, htagweb.WebServerWS, htag.runners.webhttp, htag.runners.webws) : no SEO (1st html is a "bootstrap js"), hrenderer live is not like others)

=> it's difficult to find a "common pattern" which will work, in the same manner, in all the runners

a soluce could be, to stick on websocket exchange only (so tag.update() compat for all, and change the way an htag should live). But will remove every http runner (and need to rebase the android one on ws). So every runners could work the same.

the other option : continue to have all theses differents options. But really need simplifications ! (2 hrenderer ? and runners out of htag's lib ?!)

-----

2023/08/23 : idea = Split the runners in two categories, and doc them !
- the current ones (all current runners) keeps the htag tag instance (historic way) ... named "TAG LIFE"
- special runner, which will only keep the "tag.state" ... named "STATE LIFE"

So a "TAG LIFE runner" is, de facto, a "STATE LIFE runner". But only some htag app could work in "STATE LIFE runner" : only those which base their states on tag.state.

-----

## Prob#2 Split runners packages ?
my prefered runners (which should continue to exist, in all cases ;-) )

- pyscript (which currently, supports all features) ... htag with only html is a pure joyce ;-)
- pywebview (which I don't use), will never support tag.udpate (without async in pywebview !). But useful !
- chromeapp/winapp : I prefer them, over pywebview ... because lighter, eco friendly (reuse chrome app) ... and guy's goal in the past !
- devapp : which need a rewrite ! But great concept during dev, for sure!
- htagweb : official runners for the web (*)
- androidapp : really needed to quickly deploy an apk
- browserhttp : because it doesn't need anything else than htag.

Perhaps should I leave all others ?!?

(*) : but htag.runners.webhttp, htag.runners.webws can be better than htagweb.WebServer, htagweb.WebServerWS, because one process/thread (easily share between tags).

the futur, with differents pypi libs, could be :

htag: (without dependancies) 
 - pyscript (should always come with htag module (to let htag be compatible with pyscript ootb))
 - browserhttp (futur devapp ? (but to support tag.update, need to implement websocket on my own ;-() ... and should implement ".serve", to handle multiple app (like web runners (except htagserver)))

htagweb: (starlette foundations, runners with "session" per user, ability to serve multiple app)
 - webserver   : tag.update will never be possible (because separate process should communicate in the other side too)
 - webserverws : tag.update will never be possible (because separate process should communicate in the other side too)
 - webhttp     : tag.update is not possible, because http is one direction only
 - webws       : tag.update possible !
 - htagserver (doesn't expose the ".serve" method, like others ^^, because it can auto-serve on path)

htagchrome: (new package?) (one use starlette, the other tornado)
 - chromeapp : (tag.update !)
 - winapp    : (tag.update !)

htagcef: (new package?) 
 - pywebview (with explanation about current limitations in pywebview)
 - ?a real cef runner? (like in good old 'guy')

htagandroid (new package?) (tornado/kivy based)
 - androidapp : (no tag.update yet ...)

IN ALL CASES ---> I should write efficient docs on how-to-use the "HRenderer" ... which is clearly the main piece between htag.Tag and the runner. (perhaps a "hrenderer2" (subclass) for "tag.update" feature only, to clearly separate the twos ?!)
