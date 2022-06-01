# HTag

docs are coming ....

meanwhile, you can learn a lot on [htag's demo](https://htag.glitch.me/) ;-)


## Concept

The **htag app**, the instance, is managed in python side (thru a [runner](runners)) ... and is rendered to client side (anything which can render html/js/css) thru simples **interactions** between the client side and the python side. At each states change in python side, the rendering changes are done on client side. The 2 sides are keeped synchronous !

The only thing you'll have to do is to create a htag component. This component provides basic dom manipulations, to change its content and/or bind events ....

Of course, htag components can (or must) reuse htag components, and will enforce you to create them, to separate your UI logics... and build your own set of reusable components ! That's why htag is more taggued as an "UI Toolkit to build UI tookit", than an "UI toolkit to build GUI".

The (far from) perfect example is [htbulma](https://github.com/manatlan/htbulma), which is a set of "ready-to-use htag components", to build GUI from ground. It uses **htag**, and provide UI components, usable without (too many)knowledgement of html/js/css world.

**TODO**