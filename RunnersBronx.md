# RunnersBronx

This term "Bronx" is just here to define the current troubles with "all runners". And I would like to clarify all, before releasing the long awaited "1.0" ;-)

And it bothers me ... because I can't find the way to follow ;-)

This page is just here, for me, to try to expose troubles ;-)
(it's a lot of notes)

There are several troubles:

 1) continue to provide embbeded runners with htag module ? (or make them in separate libs (like htagweb for web))
 2) Signatures differs (a bit) from a runner to another one
 3) spezialize the way it should work. Because some can use more features than others
 4) and ensure current compatibilities, or breaks all before 1.0 ?!

The current core works well ... and the HRenderer (which is not perfect) is great.

But managing all theses runners is a big pain, to make them compatible between them. And sometimes, it's not possible at all. I feel that I need to resolve this "bronx", before a "1.0" ;-)

The new "htagweb.HtagServer" is *really* top (all htag/web features, easy to maintain, robust) ... and could be better, as a simple middleware to manage htag lifespan, in a classical starlette/fastapi/django app (which could be a game changer).
But it got some severe limitations, compared to its web brothers (htagweb.WebServer, htagweb.WebServerWS, htag.runners.webhttp, htag.runners.webws) : no SEO (1st html is a crap/js), hrenderer live is not like others)

=> it's difficult to find a "common pattern" which will work, in the same manner, in all the runners

a soluce could be, to stick on websocket exchange only (so tag.update() compat for all, and change the way htag's live). But will remove every http runner (and need to rebase the android one on ws). So every runners could work the same.

the other option : continue to have all theses differents options. But really need simplifications ! (2 hrenderer ? and runners out of htag's lib ?!)

my prefered runners (which should continue to exist)

- pyscript (which currently, supports all features) ... htag with only html is a pure joyce ;-)
- pywebview (which I don't use), will never support tag.udpate (without async in pywebview !). But useful !
- chromeapp/winapp : I prefer them, over pywebview ... because lighter, eco friendly (reuse chrome app) ... and guy's goal in the past !
- devapp : which need a rewrite ! But great concept during dev, for sure!
- htagweb : official runners for the web (*)
- androidapp : really needed to quickly deploy an apk
- browserhttp : because it doesn't need anything else than htag.

Perhaps should I leave all others ?!?

(*) : but htag.runners.webhttp, htag.runners.webws can be better than htagweb.WebServer, htagweb.WebServerWS, because one process (easily share between tags).

the futur could be :

htag: (without dependancies) 
 - pyscript (should always come with htag module (to let htag be compatible with pyscript ootb))
 - browserhttp (futur devapp ? (but to support tag.update, need to implement websocket on my own ;-())

htagweb: (starlette foundations, runners with "session" per user, ability to serve multiple app)
 - webserver
 - webserverws
 - webhttp
 - webws
 - htagserver

htagchrome: (new package?) 
 - chromeapp
 - winapp

htagcef: (new package?) 
 - pywebview

htagandroid (new package?)
 - androidapp 
