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
from .tag import HTagException,Tag, BaseCaller

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
        self.tag=tag
        self._states={}

        def rec( childs ):
            for obj in childs:
                tag,childs= list(obj.items())[0]
                self._states[id(tag)] = tag._getStateImage()
                rec( childs )

        rec( [self.tag._getTree()])
        logger.debug("Stater.__init__(), save %s states", len(self._states))

    def guess(self): # -> list<Tag>
        """ to be runned after interactions to guess whose are modifieds
            return modifieds tags
        """
        logger.debug("Stater.guess(), start guessing ....")
        modifieds=[]

        def rec( childs):
            for obj in childs:
                tag,childs= list(obj.items())[0]
                state_before= self._states.get( id(tag) )
                state_after = tag._getStateImage()
                if state_after != state_before:
                    logger.debug("STATE BEFORE for %s = '%s'", repr(tag), state_before )
                    logger.debug("STATE AFTER  for %s = '%s'", repr(tag), state_after )

                    while tag.tag is None:
                        tag = tag.parent

                    if tag is None: # should be impossible
                        raise HTagException("no real parent ?!?")

                    modifieds.append(tag)
                else:
                    # no need to control childs, coz the parent will redraw all (childs too)
                    rec(childs)

        rec( [self.tag._getTree()] )
        logger.debug("Stater.guess(), modifieds components : %s", [repr(i) for i in modifieds])

        return list(tuple(modifieds))   # ensure unicity


class HRenderer:
    def __init__(self, tagClass: type, js:str, exit_callback:Optional[Callable]=None, init= ((),{}), fullerror=False, statics=[], session=None ):
        """ tag object will be setted as a 'body' tag ! """
        """ js should containt an interact method, and an initializer to call the start()"""
        if not issubclass(tagClass, Tag): raise HTagException("HRenderer can only handle tag subclasses !")
        if not isinstance(statics, list): raise HTagException("HRenderer statics should be a list !")
        self.fullerror = fullerror
        self._interaction_scripts=[]
        self.init = tuple( [tuple(init[0]),dict(init[1])] ) # save args/kargs whose initialized the instance
        self.session=session

        self.sendactions=None   # method async sendactions(actions:dict) -> bool

        try:
            try:
                args,kargs = init
                tag = tagClass( *args,_hr_=self,**kargs )
            except TypeError:
                logger.warning(f"Can't instanciate tag '{tagClass.__name__}' with {init} arguments, so instanciate it without argument !")
                tag = tagClass(_hr_=self)
        except Exception as e:
            print("ERROR",e)
            stacktrace=traceback.format_exc()
            logger.error("Exception %s:\n%s", e, stacktrace)
            tag=Tag.body(f"init error : {e}",js="document.title='HTag Error'")

        self.tag=tag
        self.tag.tag="body" # force first tag as body !!
        if exit_callback:
            # add an .exit() method on the tag !!!!!!!!!!!!!!!!!!!!!!
            self.tag.exit = exit_callback

        self._statics: list = list(statics)

        ensureList=lambda x: list(x) if type(x) in [list,tuple] else [x]

        def feedStatics(tag): # tag can be an instance or a class

            def detectStatics(c):
                ll=[]
                if hasattr(c,"__bases__"):
                    scan = c.__bases__
                else:
                    scan = c.__class__.__bases__
                for i in scan:
                    if issubclass(i,Tag):
                        ll.extend( ensureList(i.statics) )
                ll.extend(ensureList(c.statics))
                return ll

            def appendIfNotPresent(tag):
                if tag._hash_ not in [i._hash_ for i in self._statics]:
                    self._statics.append( tag )

            for i in detectStatics(tag):
                if isinstance(i,Tag):
                    appendIfNotPresent(i)
                elif isinstance(i,str): # auto add as Tag.style // CSS
                    appendIfNotPresent( Tag.style(i))
                elif isinstance(i,bytes): # auto add as Tag.script // JS
                    appendIfNotPresent( Tag.script(i.decode()))
                else:
                    raise HTagException(f"Included static is bad {i}")


        if hasattr(tagClass, "imports") and tagClass.imports is not None:
            # there is an "imports" attribut
            # so, try to import statics according "imports" attrs on tags
            logger.info("Include statics from Tag's imports attibut")
            feedStatics(tagClass)
            def rec1( tagc ):
                if hasattr(tagc, "imports") and tagc.imports is not None:
                    imports = ensureList(tagc.imports)
                    if not all([isinstance(c,type) and issubclass(c,Tag) for c in imports]):
                        raise HTagException("imports can contains only Tag classes %s" % imports)
                    for c in imports:
                        feedStatics(c)
                        rec1(c)

            rec1( tagClass )
        else:
            # there is no "imports" attribut
            # so try to imports statics using Tag subclasses
            logger.info("Include statics from Tag's subclasses")
            def rec2( cls ):
                for c in cls.__subclasses__():
                    feedStatics(c)
                    rec2(c)

            rec2(Tag)

        logger.debug("HRenderer(), statics found : %s", [repr(i) for i in self._statics])

        startjs="\n".join(tag._getAllJs() + self._interaction_scripts)
        self._interaction_scripts=[]    # reset the list !

        js_base="""
function start() { %s }

function _error(txt,env) {
    if(window.error)
        error( env+" ERROR: "+txt );
    else
        console.log( env+" ERROR:", txt );
    throw txt; // throw the js/py execption in the js console (and stop the process)
}

function try_js( code ) {
    try{ eval( code ) }
    catch(e) {
        _error(e, "JS");
    }
}


function action( payload ) {
    let o;
    if(typeof payload == "string") {
        try {
            o=JSON.parse(payload);
        } catch(e) {
            // it's not json (so a big python error, or an http trouble)
            _error( payload, "COM"); // so it's a COM error (an interaction returning other than json)
        }
    }
    else // ensure compat with old system (PyWebView here!)
        o = payload;

    if(o.hasOwnProperty("update"))
        Object.keys(o["update"]).forEach(key => {
            if(key==0)
                document.body.outerHTML = o["update"][0];
            else
                document.getElementById( key ).outerHTML = o["update"][key];
        });
    if(o.hasOwnProperty("stream"))
        Object.keys(o["stream"]).forEach(key => {
            document.getElementById( key ).innerHTML += o["stream"][key];
        });

    if(o.hasOwnProperty("post")) try_js(o["post"]);
    if(o.hasOwnProperty("next")) try_js(o["next"]);
    if(o.hasOwnProperty("err")) _error( o["err"], "PYTHON")
}

function jevent(e) {
    let n={};
    if(e!==undefined && e!=null && e)
        for (let k in e) {
            let v=e[k];
            let t=typeof v;
            if( k.toUpperCase()!=k && (t === "number" || t === "boolean" || t === "string") )
                n[k] = v;
        }
    return n;
}

%s
""" % ( startjs , js.replace("<<hrid>>",str(id(self))))   # I DONT LIKE THAT !

        self._statics.append( Tag.script( js_base ))

        self._loop={}   # for savng generator, to keep them during GC


    def _addInteractionScript(self, js:str):
        self._interaction_scripts.append(js)

    async def interact(self,oid,method_name:str,args,kargs,event=None) -> dict:
        """ call the 'method_name' of pyobj 'id' with (args,kargs), return the pyobj/tag"""
        try:
            ## self._interaction_scripts=[] # reset the list
            next_js_call=None

            state = Stater(self.tag)
            obj = Tag.find_tag(oid)
            if obj:
                obj._event=event or {}

                # call the method
                method=getattr(obj,method_name)

                logger.info(f"INTERACT with METHOD {fmtcaller(method_name,args,kargs)}, of %s", repr(obj) )

                if asyncio.iscoroutinefunction( method ):
                    r=await method(*args,**kargs)
                else:
                    r=method(*args,**kargs)

                if isinstance(r, types.AsyncGeneratorType) or isinstance(r, types.GeneratorType):
                    # save it, to avoid GC
                    self._loop[id(r)] = dict(gen=r,tag=obj)

            else:
                obj = self._loop.get(oid,None)
                if obj: # it's a existing generator
                    r, obj = obj["gen"], obj["tag"]
                    logger.info("INTERACT with GENERATOR %s(...), of %s",r.__name__, repr(obj) )
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

            rep= self._mkReponse(state.guess() )

            if ret:
                obj.add(ret) # add content in object
                if not isinstance(ret,str) and hasattr(ret,"__iter__"):
                    rep.setdefault("stream",{})[ id(obj) ] = "".join([str(i) for i in ret])
                else:
                    rep.setdefault("stream",{})[ id(obj) ] = str(ret)


            # --> rep
            if self._interaction_scripts:
                # some js scripts was generated during interactions
                if "post" not in rep:
                    rep["post"]=""
                # add them
                rep["post"] += "\n".join(self._interaction_scripts)

                self._interaction_scripts=[]    # reset the list !

            if next_js_call:
                # if there was generator, set the next js call !
                rep["next"]= str(next_js_call)

        except Exception as e:
            print("ERROR",e)
            stacktrace=traceback.format_exc()
            logger.error("Exception %s:\n%s", e, stacktrace)
            rep={"err": stacktrace if self.fullerror else str(e) }

        logger.info("RETURN --> %s",json.dumps(rep,indent=4))

        return rep

    def _mkReponse(self, tags:list) -> dict: # can't set a "script" key -> so named "post" (coz guy)
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

    async def update(self,tag:Tag):
        """ return True if hrenderer can update the component (ex: runner with ws)"""
        if self.sendactions is None:
            logger.error("This runner can't update a component")
        else:
            # generate actions (.js and update/rendering )
            actions=self._mkReponse( [tag] )

            # add eventuals interactions scripts (and reset them)
            if self._interaction_scripts:
                # some js scripts was generated during interactions
                if "post" not in actions:
                    actions["post"]=""
                # add them
                actions["post"] += "\n".join(self._interaction_scripts)

                self._interaction_scripts=[]    # reset the list !

            return await self.sendactions( actions )
        return False

    def __str__(self) -> str:
        head=Tag.head()
        head += Tag.meta(_charset="utf-8")
        head += Tag.meta(_name="viewport",_content="width=device-width, initial-scale=1")
        head += Tag.meta(_name="version",_content=f"htag {__version__}")
        for i in self._statics:
            head.add(i,True)    # force reparenting
        head += Tag.title( self.title )   # set a default title

        return "<!DOCTYPE html>"+str(Tag.html( head+str(self.tag) ))

    @property
    def title(self) -> str:
        return self.tag.__class__.__name__


