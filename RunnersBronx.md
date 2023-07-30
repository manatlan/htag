# RunnersBronx

This term "Bronx" is just here to define the current troubles with "all runners". And I would like to clarify all, before releasing the long awaited "1.0" ;-)

And it bothers me ... because I can't find the way to follow ;-)

This page is just here, for me, to try to expose troubles ;-)

There are several troubles:

 1) continue to provide embbeded runners with htag module ? (or make them in separate libs (like htagweb for web))
 2) Signatures differs (a bit) from a runner to another one
 3) spezialize the way it should work. Because some can use more features than others
 4) and ensure current compatibilities, or breaks all before 1.0 ?!

The current core works well ... and the HRenderer (which is not perfect) is great.

But managing all theses runners is a big pain, to make them compatible between them. And sometimes, it's not possible at all. I feel that I need to resolve this "bronx", before a "1.0" ;-)

The new "htagweb.HtagServer" is *really* top (all htag/web features, easy to maintain, robust) ... and could be better, as a simple middleware to manage htag lifespan, in a classical starlette/fastapi/django app (which could be a game changer).
But it got some sever limitations, compared to its web brothers (htagweb.WebServer, htagweb.WebServerWS, htag.runners.webhttp, htag.runners.webws) 
