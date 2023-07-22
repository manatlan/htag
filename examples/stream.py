import os,sys; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))

from htag import Tag # the only thing you'll need ;-)
import asyncio

"""
This example is for "htag powerusers" ...
If you discovering the project, come back here later ;-)
(just keep in mind, that it's possible to output a large amount of data, in a decent way)

It shows you the "htag way" to create a component which
can output a large amount of data (outputed from an async source)
without rendering all the object at each yield statement !
(ex: rendering an http paging, or an apache httpd log ...)

It use a "htag mechanism" which use the yield to add an object in.
this mechanism is named "stream"

"""

async def asyncsource():
    """ this is an async source (which simulate delay to get datas) """
    for i in range(3):
        yield "line %s" % i
        await asyncio.sleep(0.2)    # simulate delay from the input source


class Viewer(Tag.ul):
    """ Object which render itself using a async generator (see self.feed)
        (the content is streamed from an async source)
    """
    def __init__(self):
        super().__init__(_style="border:1px solid red")


    async def feed(self):
        """ async yield object in self (stream)"""
        self.clear()
        async for i in asyncsource():
            yield Tag.li(i) # <- automatically added to self instance /!\

    async def feed_bad(self):
        """ very similar (visually), but this way IS NOT GOOD !!!!
            because it will render ALL THE OUTPUT at each yield !!!!!
        """
        self.clear()
        async for i in getdata():
            self <= Tag.li(i) # manually add
            yield             # and force output all !


class Page(Tag.body):

    def init(self):

        self.view = Viewer()
        self <= self.view

        # not good result (yield in others space)
        self <= Tag.button( "feed1", _onclick= lambda o: self.view.feed()  )                # in the button
        self <= Tag.button( "feed2", _onclick= self.bind( lambda o: self.view.feed() ) )    # in Page

        # good result (yield in the viewer)
        self <= Tag.button( "feed3", _onclick= self.view.bind( self.view.feed ) )
        self <= Tag.button( "feed4", _onclick= self.view.bind.feed() )

App=Page
if __name__=="__main__":
    # import logging
    # logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
    # logging.getLogger("htag.tag").setLevel( logging.INFO )

    # and execute it in a pywebview instance
    from htag.runners import *

    # here is another runner, in a simple browser (thru ajax calls)
    BrowserHTTP( Page ).run()
    # PyWebWiew( Page ).run()
