# HTag

docs are coming ....

meanwhile, you can learn a lot on [htag's demo](https://htag.glitch.me/) ;-)


## Concept

The **htag app**, the instance, is managed in python side (thru a [runner](runners)) ... and is rendered to client side (anything which can render html/js/css) thru simples **interactions** between the client side and the python side. At each states change in python side, the rendering changes are done on client side. The 2 sides are keeped synchronous !

The only thing you'll have to do is to create a htag component. This component provides basic dom manipulations, to change its content and/or bind events ....

**TODO**