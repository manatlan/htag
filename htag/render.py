# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################
import json,asyncio,types,traceback

from . import __version__
from .tag import HTagException,H, Tag, TagBase, BaseCaller

from typing import Callable, Optional

StrNonable = Optional[str]


import logging
logger = logging.getLogger(__name__)

def fmtcaller(method:str,a,k) -> str:
    """ pretty format caller method( a:tuple, k:dict) -> str"""
    MAX=15
    def show(x):
        if isinstance(x,str):
            if len(x)>=MAX:
                x=x[:MAX-3]+"..."
            return json.dumps(x)
        elif isinstance(x,bytes):
            if len(x)>=MAX:
                x= x[:MAX-3]+b"..."
        return str(x)

    args = [show(i) for i in a]+[f"{k}={show(v)}" for k,v in k.items()]
    return f'{method}( %s )' % ", ".join(args)

class Stater:
    """ Class to save all states of 'tag' and children/embbeded Tags, before interaction!
        so, after interaction : .guess() can guess modified one
        (intelligent rendering)
    """
    def __init__(self, tag: Tag ):
        logger.debug("Stater.__init__(), save state before interactions ")
        self.tag=tag
        self._states={}

        def rec( childs ):
            for obj in childs:
                tag,childs= list(obj.items())[0]
                self._states[id(tag)] = tag._getStateImage()
                rec( childs )

        rec( [self.tag._getTree()])
        logger.debug("Stater.__init__(), save %s states", len(self._states))

    def guess(self,dontRedraw=Optional[Tag]): # -> list<Tag>
        """ to be runned after interactions to guess whose are modifieds
            return modifieds tags
        """
        logger.debug("Stater.guess(), start guessing ....")
        modifieds=[]

        def rec( childs):
            for obj in childs:
                tag,childs= list(obj.items())[0]
                state_after = tag._getStateImage()
                state_before= self._states.get( id(tag) )
                if state_after != state_before:
                    if id(tag)==id(dontRedraw):
                        logger.debug("Don't redraw %s (but modified)", repr(dontRedraw))
                        # but perhaps childs ...
                        rec(childs)
                    else:
                        logger.debug("STATE BEFORE for %s = '%s'", repr(tag), state_before )
                        logger.debug("STATE AFTER  for %s = '%s'", repr(tag), state_after )
                        modifieds.append(tag)
                else:
                    # no need to see childs, coz the parent will redraw all (childs too)
                    rec(childs)

        rec( [self.tag._getTree()] )
        logger.debug("Stater.guess(), modifieds components : %s", [repr(i) for i in modifieds])
        return modifieds


class HRenderer:
    def __init__(self, tag: Tag, js:str, exit_callback:Optional[Callable]=None):
        """ tag object will be setted as a 'body' tag ! """
        """ js should containt an interact method, and an initializer to call the start()"""
        if not isinstance(tag, Tag): raise HTagException("Can only render a Tag !")
        self.tag=tag
        self.tag.tag="body" # force first tag as body !!
        if exit_callback:
            # add an .exit() method on the tag !!!!!!!!!!!!!!!!!!!!!!
            self.tag.exit = exit_callback

        self._statics: list = []

        ensureList=lambda x: list(x) if type(x) in [list,tuple] else [x]

        def feedStatics(tag):
            for i in ensureList(tag.statics):
                if isinstance(i,TagBase):
                    if isinstance(i,Tag):
                        logger.warning("Avoid to include dynamic Tag in statics! (it will be converted)")
                        i = i._ensureTagBase()

                    if i.md5 not in [j.md5 for j in self._statics]:
                        self._statics.append( i )
                # else:
                #     raise HTagException("Statics must be a TagBase/H")


        if hasattr(self.tag, "imports") and self.tag.imports is not None:
            # there is an "imports" attribut
            # so, try to import statics according "imports" attrs on tags
            logger.info("Include statics from Tag's imports attibut")
            feedStatics(tag)
            def rec( tag ):
                if hasattr(tag, "imports") and tag.imports is not None:
                    imports = ensureList(tag.imports)
                    if not all([isinstance(c,type) and issubclass(c,TagBase) for c in imports]):
                        raise HTagException("imports can contains only Tag classes")
                    for c in imports:
                        feedStatics(c)
                        rec(c)

            rec( self.tag )
        else:
            # there is no "imports" attribut
            # so try to imports statics using Tag subclasses
            logger.info("Include statics from Tag's subclasses")
            def rec( tag ):
                for c in tag.__subclasses__():
                    feedStatics(c)
                    rec(c)

            rec(Tag)

        logger.debug("HRenderer(), statics found : %s", [repr(i) for i in self._statics])

        js_base="""
function start() { %s }

function action( o ) {

    if(o.hasOwnProperty("update"))
        Object.keys(o["update"]).forEach(key => {
            document.getElementById( key ).outerHTML = o["update"][key];
        });
    if(o.hasOwnProperty("stream"))
        Object.keys(o["stream"]).forEach(key => {
            document.getElementById( key ).innerHTML += o["stream"][key];
        });

    if(o.hasOwnProperty("post")) eval( o["post"] );
    if(o.hasOwnProperty("next")) eval( o["next"] );
    if(o.hasOwnProperty("err"))  console.log( "ERROR", o["err"] );
}

%s
""" % (BaseCaller( None ), js)

        self._statics.append( H.script( js_base ))

        self._loop={}   # for savng generator, to keep them during GC

    async def interact(self,oid,method_name:str,args,kargs) -> dict:
        """ call the 'method_name' of pyobj 'id' with (args,kargs), return the pyobj/tag"""
        try:
            interaction_scripts=[] # interact js scripts
            next_js_call=None

            if oid==0:
                # start (not a real interaction, just produce the first rendering of the main tag (will be a body))
                logger.info("INTERACT INITIAL: %s",repr(self.tag))
                rep = self._mkReponse( [self.tag] )
                rep["update"]={0: list(rep["update"].values())[0]}  #INPERSONNATE (for first interact on id#0)
            else:
                def hookInteractScripts(obj,js:str):
                    interaction_scripts.append( obj._genIIFEScript(js) ) #IIFE !

                state = Stater(self.tag)
                setattr(Tag,"__call__", hookInteractScripts) # not great (with concurrencies)
                try:
                    norender=False

                    obj = Tag.find_tag(oid)
                    if obj:
                        # call the method
                        method=getattr(obj,method_name)

                        norender = hasattr(method,"_norender")

                        logger.info(f"INTERACT with METHOD {fmtcaller(method_name,args,kargs)} %s, of %s", "**NoRender**" if norender else "", repr(obj) )

                        if asyncio.iscoroutinefunction( method ):
                            r=await method(*args,**kargs)
                        else:
                            r=method(*args,**kargs)

                        if isinstance(r, types.AsyncGeneratorType) or isinstance(r, types.GeneratorType):
                            # save it, to avoid GC (and save the Tag/norender)
                            self._loop[id(r)] = dict(gen=r,tag=obj,norender= norender)

                    else:
                        obj = self._loop.get(oid,None)
                        if obj: # it's a existing generator
                            r, obj, norender = obj["gen"], obj["tag"], obj["norender"]
                            logger.info("INTERACT with GENERATOR %s(...) %s, of %s",r.__name__, "**NoRender**" if norender else "", repr(obj) )
                        else:
                            raise Exception(f"{oid} is not an existing Tag or generator (dead objects ?)?!")

                    ret=None
                    if isinstance(r, types.AsyncGeneratorType):
                        # it's a "async def yield"
                        try:
                            ret = await r.__anext__()
                            next_js_call = BaseCaller(r)
                        except StopAsyncIteration:
                            del self._loop[ id(r) ]
                    elif isinstance(r, types.GeneratorType):
                        # it's a "def yield"
                        try:
                            ret = r.__next__()
                            next_js_call = BaseCaller(r)
                        except StopIteration:
                            del self._loop[ id(r) ]
                    else:
                        # it's a simple method
                        assert r is None
                        ret=None

                    if norender:
                        rep= self._mkReponse(state.guess(obj) ) # avoid redraw obj
                    else:
                        rep= self._mkReponse(state.guess() )

                    if ret:
                        obj.add(ret) # add content in object
                        if not isinstance(ret,str) and hasattr(ret,"__iter__"):
                            rep.setdefault("stream",{})[ id(obj) ] = "".join([str(i) for i in ret])
                        else:
                            rep.setdefault("stream",{})[ id(obj) ] = str(ret)

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
                rep["next"]= str(next_js_call)

        except Exception as e:
            print("ERROR",e)
            logger.error("Exception %s:\n%s", e, traceback.format_exc())
            rep={"err": str(e) }

        logger.info("RETURN --> %s",json.dumps(rep,indent=4))

        return rep

    def _mkReponse(self, tags) -> dict: # can't set a "script" key -> so named "post" (coz guy)
        rep={}

        scripts = []
        updates={}

        if tags:
            logger.debug("Force Tag rendering (for response): %s",[repr(i) for i in tags])
            for tag in tags:
                updates[id(tag)]=str(tag)

                if isinstance(tag,Tag):
                    scripts.extend( tag._getAllJs() )

        if updates:
            rep["update"]=updates

        if scripts:
            rep["post"]="\n".join( scripts )

        return rep

    def __str__(self) -> str:
        head=H.head()
        head <= H.meta(_charset="utf-8")
        head <= H.meta(_name="viewport",_content="width=device-width, initial-scale=1")
        head <= H.meta(_name="version",_content=f"HTag {__version__}")
        head <= H.title( self.title )
        head <= self._statics

        body=H.body( "Loading...", _id=0 ) # IMPERSONATE (first interact on id #0)
        return "<!DOCTYPE html>"+str(H.html( [head,body] ))

    @property
    def title(self) -> str:
        return self.tag.__class__.__name__


