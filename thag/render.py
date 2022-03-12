# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/thag
# #############################################################################
import json,ctypes,asyncio,types

from . import __version__
from .tag import Tag, genJsInteraction

class Stater:
    """ Class to save all states of 'tag' and children/embbeded Tags, before interaction!
        so, after interaction : .guess() can guess modified one
        (intelligent rendering)
    """
    def __init__(self, tag: Tag ):
        self.tag=tag
        self._states={}

        def rec( childs ):
            for obj in childs:
                tag,childs= list(obj.items())[0]
                self._states[id(tag)] = tag._getStateImage()
                rec( childs )

        rec( [self.tag._getTree()])

    def guess(self): # -> list<Tag>
        """ to be runned after interactions to guess whose are modifieds
            return modifieds tags
        """
        modifieds=[]

        def rec( childs):
            for obj in childs:
                tag,childs= list(obj.items())[0]
                state = tag._getStateImage()
                if state != self._states.get( id(tag) ):
                    # print("AVANT",self._states.get( id(tag) ))
                    # print("APRES",state)
                    # state has changed
                    modifieds.append(tag)
                else:
                    # no need to see childs, coz the parent will redraw all (childs too)
                    rec(childs)

        rec( [self.tag._getTree()] )
        return modifieds


class HRenderer:
    def __init__(self, tag: Tag, js:str, exit_callback=None):
        """ tag object will be setted as a 'body' tag ! """
        """ js should containt an interact method, and an initializer to call the start()"""
        assert isinstance(tag, Tag)
        self.tag=tag
        self.tag.tag="body" # force first tag as body !!
        if exit_callback:
            # add an .exit() method on the tag !!!!!!!!!!!!!!!!!!!!!!
            self.tag.exit = exit_callback

        # get all statics in the tree from the root tag
        children=[]
        if isinstance( tag, Tag):
            def rec( childs ):
                for obj in childs:
                    tag,childs= list(obj.items())[0]
                    children.append(tag)
                    rec( childs )
            rec( [self.tag._getTree()])

        # compute a real list of unique import
        self._statics=[]
        for child in children:
            if isinstance(child,Tag):
                statics = child.statics if type(child.statics )==list else [child.statics ]
                for i in statics:
                    if getattr(i,"md5") not in [j.md5 for j in self._statics]:
                        self._statics.append( i )

        js_base="""
function start() { %s }

function action( o ) {

    if(o.hasOwnProperty("update"))
        o["update"].forEach( i => {
            document.getElementById( i["id"] ).outerHTML = i["content"]
        })

    if(o.hasOwnProperty("post"))    eval( o["post"] );
    if(o.hasOwnProperty("next"))    eval( o["next"] );
}

%s
""" % (genJsInteraction(0), js)

        self._statics.append( Tag.script( js_base ))

        self._loop={}   # for savng generator, to keep them during GC

    async def interact(self,oid,method_name,args,kargs) -> dict:
        """ call the 'method_name' of pyobj 'id' with (args,kargs), return the pyobj/tag"""
        interaction_scripts=[] # interact js scripts
        next_js_call=None

        if oid==0:
            # start (not a real interaction, just produce the first rendering of the main tag (will be a body))
            print("INTERACT INITIAL:",repr(self.tag))
            rep = self._mkReponse( [self.tag] )
            rep["update"][0]["id"] = 0  #INPERSONNATE (for first interact on id#0)
        else:
            obj = ctypes.cast(oid, ctypes.py_object).value    # /!\

            def hookInteractScripts(obj,js):
                interaction_scripts.append( obj._genIIFEScript(js) ) #IIFE !

            state = Stater(self.tag)
            setattr(Tag,"__call__", hookInteractScripts) # not great (with concurrencies)
            try:
                if isinstance(obj,Tag):
                    print("INTERACT with",repr(obj),f", calling: {method_name}({args},{kargs})")

                    # call the method
                    method=getattr(obj,method_name)

                    if asyncio.iscoroutinefunction( method ):
                        r=await method(*args,**kargs)
                    else:
                        r=method(*args,**kargs)
                else:
                    print("INTERACT with GENERATOR",obj.__name__)
                    r=obj

                if isinstance(r, types.AsyncGeneratorType):
                    # it's a "async def yield"
                    self._loop[id(r)] = r # save it, to avoid GC
                    try:
                        await r.__anext__()
                        next_js_call = genJsInteraction(id(r))
                    except StopAsyncIteration:
                        del self._loop[ id(r) ]
                elif isinstance(r, types.GeneratorType):
                    # it's a "def yield"
                    self._loop[id(r)] = r # save it, to avoid GC
                    try:
                        r.__next__()
                        next_js_call = genJsInteraction(id(r))
                    except StopIteration:
                        del self._loop[ id(r) ]
                else:
                    # it's a simple method
                    assert r is None

                rep= self._mkReponse(state.guess() )

            finally:
                # clean the (fucking) situation ;-)
                try: # to avoid del trouble in multi concurency
                    del Tag.__call__
                except AttributeError:
                    pass

        # --> rep
        if interaction_scripts:
            # some js scripts was generated during interactions
            if "post" not in rep:
                rep["post"]=""
            # add them
            rep["post"] += "\n".join(interaction_scripts)

        if next_js_call:
            # if there was generator, set the next js call !
            rep["next"]=next_js_call

        print("--->",json.dumps(rep,indent=4))

        return rep


    def _mkReponse(self, tags) -> dict: # can't set a "script" key -> so named "post" (coz guy)
        rep={}

        scripts = []

        if tags:
            rep["update"]=[]
            for tag in tags:
                html = str(tag)
                if isinstance(tag,Tag):
                    scripts.extend( tag._getAllJs() )
                rep["update"].append( dict(id=id(tag),content=html) )

        if scripts:
            rep["post"]="\n".join( scripts )

        return rep

    def __str__(self) -> str:
        head=Tag.head()
        head <= Tag.meta(_charset="utf-8")
        head <= Tag.meta(_name="viewport",_content="width=device-width, initial-scale=1")
        head <= Tag.meta(_name="version",_content=f"Thag {__version__}")
        head <= Tag.title( self.title )
        head <= self._statics

        body=Tag.body( "Loading...", _id=0 ) # #INPERSONNATE (first interact on id #0)
        return "<!DOCTYPE html>"+str(Tag.html( [head,body] ))

    @property
    def title(self):
        return self.tag.__class__.__name__



