# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################
import html,json,hashlib
import logging,types,asyncio
import weakref
from typing import Sequence,Union,Optional,Any,Callable,Type

AnyTags = Union[ Optional[Any], Sequence[Any]]
StrNonable = Optional[str]

logger = logging.getLogger(__name__)

class HTagException(Exception): pass

md5= lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()

def stringify(obj):
    def my(obj):
        if isinstance(obj,bytes): # trick to convert b'' -> pure javascript
            return "<:<:%s:>:>" % obj.decode()
    return json.dumps(obj, default=my).replace('"<:<:',"").replace(':>:>"',"")


class Elements(list):
    def __add__(self,  elt: AnyTags):
        if elt is None:
            pass
        elif not isinstance(elt,str) and hasattr(elt,"__iter__"):
            self.extend( list(elt) )
        else:
            self.append(elt)
        return self
    def __radd__(self,  elt: AnyTags):
        if elt is None:
            pass
        elif not isinstance(elt,str) and hasattr(elt,"__iter__"):
            self[:0] = list(elt)
        else:
            self.insert(0,elt)
        return self

class TagBase:
    """ This is a class helper to produce a "HTML TAG" """
    tag: str="div" # default one

    def __init__(self, content:AnyTags=None,**_attrs):
        self.set(content)

        self._attrs={}
        for k,v in _attrs.items():
            if not k.startswith("_"):
                raise HTagException(f"Can't set attributs without underscore ('{k}' should be '_{k}')") # for convention only ;-(
            else:
                self[ k[1:].replace("_","-") ] = v

        # compute a md5 (to indentify state for statics only now)
        # WARN : attrs or content change -> doesn't affect md5 !
        self.md5 = md5( str(self._attrs) + str(self._childs))

    def __le__(self, elt: AnyTags ):
        self.add(elt)
        return elt

    def __iadd__(self,  elt: AnyTags):
        ''' use "+=" instead of "<=" '''
        self.add(elt)
        return self

    def __add__(self,  elt):
        return Elements([self]) + elt
    def __radd__(self,  elt):
        return elt + Elements([self])

    def clear(self):
        self._childs=Elements()

    def set(self,elt:AnyTags):
        """ a bit like .innerHTML setting (avoid clear+add)"""
        self.clear()
        self.add( elt)

    def add(self,elt:AnyTags):
        """ add an object or a list/tuple of objects """
        self._childs.__add__(elt)

    @property
    def childs(self) -> list:
        return self._childs

    @property
    def attrs(self) -> dict:
        return self._attrs

    def __setitem__(self,attr:str,value):
        # if not isinstance(self,Tag):  #TODO: in the future ;-)
        #     raise HTagException("Can't assign a callback on a tagbase")
        self._attrs[attr]=value

    def __getitem__(self,attr:str) -> Any:
        return self._attrs.get(attr,None)

    def __str__(self):
        return self.__render__( list(self._attrs.items()) , str )

    def __render__(self, attrs:list, mystr:Callable ) -> str:
        rattrs=[]
        for k,v in attrs:
            if v is not None:
                if isinstance(v,bool):
                    if v == True:
                        rattrs.append(k)
                else:
                    rattrs.append( '%s="%s"' % (k,html.escape( str(v) )) )
        return """<%(tag)s%(attrs)s>%(content)s</%(tag)s>""" % dict(
            tag=self.tag.replace("_","-"),
            attrs=" ".join([""]+rattrs) if rattrs else "",
            content="".join([mystr(i) for i in self._childs if i is not None]),
        )



    def _getStateImage(self) -> str: #TODO: could disapear (can make something more inteligent here!)
        """Return a str'image (state) of the object, for quick detection (see Stater())"""

        logger.debug("Force Tag rendering (for state image): %s",repr(self))
        str(self) # force a re-rendering (for builded lately)

        image=lambda x: "[%s]"%id(x) if isinstance(x,Tag) else str(x)
        return """%s%s:%s""" % (
            self.tag,
            self._attrs,
            [image(i) for i in self._childs],
        )

    def _getTree(self) -> dict:
        """ return a tree of TagBase childs """
        ll=[]

        for i in self._childs:
            if isinstance(i,TagBase):
                ll.append( i._getTree() )

        return {self:ll}

    def __repr__(self):
        return f"<{self.__class__.__name__}'{self.tag} {self._attrs.get('id')} (childs:{len(self._childs)})>"

    def _ensureTagBase(self): # TODO: can do a lot better here !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        """ ensure that the tag/tagbase will be rendered as a real tagbase (and childs too) """
        if isinstance(self,Tag): # it REMOVES @ID !!!
            attrs = {"_"+k:v for k,v in self.attrs.items() if k != "id" }
        else:
            attrs = {"_"+k:v for k,v in self.attrs.items()}
        contents = [(i._ensureTagBase() if isinstance(i,TagBase) else i) for i in self.childs]
        t=TagBase( contents, **attrs )
        t.tag = self.tag
        return t



class TagBaseCreator(type):
    def __getattr__(self,name:str) -> Type:
        return type('TagBase%s' % name.capitalize(), (TagBase,), {**TagBase.__dict__,"tag":name})

class H(metaclass=TagBaseCreator): # Html
    def __init__(self):
        raise HTagException("no!")



class TagCreator(type):
    def __getattr__(self,name:str) -> Type:
        if name == "H":
            return H
        else:
            return type('Tag%s' % name.capitalize(), (Tag,), {**Tag.__dict__,"tag":name})

class Caller:
    def __init__(self,instance, callback:Callable, args, kargs):
        if not callable(callback): raise HTagException("The caller must be callable !")
        self.instance = instance
        self.callback = callback
        self.args = args
        self.kargs = kargs

        self._others=[]
        self._assigned = None

    def prior(self,callback:Callable,*args,**kargs):
        """ make the current (those params) first, and move the previous in _others
            (only the instance keep the same !)
        """
        self._others.append( (self.callback,self.args,self.kargs) )
        self.callback = callback
        self.args = args
        self.kargs = kargs
        return self

    def bind(self,callback:Callable,*args,**kargs): # -> Caller
        if callback is None : # do nothing
            return self
        else:
            if not callable(callback): raise HTagException("The caller must be callable !")
            if any( [isinstance(i,bytes) for i in args] ) or any( [isinstance(i,bytes) for k,i in kargs.items()] ):
                raise HTagException("Can't bind (bytes)'js_arg' in next binders !")
            self._others.append( (callback,args,kargs) )
            return self

    def assignEventOnTag(self, object, event:str):
        self._assigned = "%s-%s" % (event,id(object)) # unique identifier for the event 'event' of the tag 'object'
        self.instance._callbacks_[self._assigned]=self   # save the Caller in _callbacks_ of self.instance
        return self

    def __str__(self) -> str:
        if not self._assigned:
            raise HTagException("Caller can't be serizalized, it's not _assign'ed to an event !")
        newargs = tuple([self._assigned]+list(self.args))
        return str(BaseCaller(self.instance,"__on__", newargs, self.kargs))

class BaseCaller:
    def __init__(self,instance, mname:StrNonable=None, args=None, kargs=None):
        self.instance = instance
        self.mname = mname
        self.args = args
        self.kargs = kargs

    def __str__(self) -> str:
        interact=dict(id=0,method=self.mname,args=self.args,kargs=self.kargs)
        if self.instance is not None: interact["id"]=id(self.instance)
        return f"""interact( {stringify(interact)} );"""

class Binder:
    def __init__(self,btag_instance):
        self.__instance=btag_instance
    def __getattr__(self,method:str):
        m=hasattr(self.__instance,method) and getattr(self.__instance,method)
        if m and callable( m ):
            def _(*args,**kargs) -> BaseCaller:
                return BaseCaller(self.__instance,method,args,kargs)
            return _
        else:
            raise HTagException("Unknown method '%s' in '%s'"%(method,self.__instance.__class__.__name__))

    def __call__(self,callback:Callable,*args,**kargs) -> Caller:
        return Caller(self.__instance,callback,args,kargs)


class Tag(TagBase,metaclass=TagCreator): # custom tag (to inherit)
    statics: list = [] # list of "Tag", imported at start in html>head
    imports = None
    hr = None
    parent = None

    __instances__ = weakref.WeakValueDictionary()

    js: StrNonable = None  # post script, useful for js/init when tag is rendered

    @classmethod
    def find_tag(cls, obj_id:int):
        return cls.__instances__.get(obj_id, None)

    def __init__(self, *args,**kargs):
        self._callbacks_={}
        attrs={}
        selfs={}
        for k,v in kargs.items():
            if k.startswith("_"):
                attrs[k]=v
            elif k=="hr":       # provided by the HRenderer when instanciating the Tag !
                self.hr = v
            else:
                selfs[k]=v

        # own a simplified init() ?
        init=None
        if hasattr(self,"init"):
            init = getattr(self,"init")
            init = init if callable(init) else None

        if "_id" in attrs:
            raise HTagException("can't set the html attribut '_id'")
        else:
            the_id = id(self)
            attrs["_id"]=the_id   # force an @id !
            if init:
                TagBase.__init__(self, None, **attrs)
                init(*args,**selfs)
            else:
                # if no own 'init' method, declare default args (selfs) as attributs instance
                self.__dict__.update(selfs)

                TagBase.__init__(self, *args, **attrs)
            Tag.__instances__[the_id]=self

    # new mechanism (could replace self.bind.<m>()) ... one day
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    async def __on__(self,eventjs:str,*a,**ka):
        logger.info(f"callback __on__ {eventjs} {a} {ka}")
        caller = self._callbacks_[eventjs]

        for method,a,ka in [(caller.callback,a,ka)] + caller._others:
            if hasattr(method, '__self__') and method.__self__ == self:
                if asyncio.iscoroutinefunction( method ):
                    r=await method(*a,**ka)
                else:
                    r=method(*a,**ka)
            else:
                if asyncio.iscoroutinefunction( method ):
                    r=await method(self,*a,**ka)
                else:
                    r=method(self,*a,**ka)

            if isinstance(r, types.AsyncGeneratorType):
                async for i in r:
                    yield i
            elif isinstance(r, types.GeneratorType):
                for i in r:
                    yield i
            else:
                assert r is None

    def __setitem__(self,attr:str,value):
        if type(value) in [types.FunctionType,types.MethodType]:
            value = Caller( self, value, (), {})
            value.assignEventOnTag( self, attr )
            logger.info("Assign event '%s' (simple callback) on %s" % (attr,repr(self)))
        elif isinstance(value,Caller):
            value.assignEventOnTag( self, attr )
            logger.info("Assign event '%s' (handled) on %s" % (attr,repr(value.instance)))

        TagBase.__setitem__(self,attr,value)
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


    @property
    def bind(self):
        """ to bind method ! and return its js repr"""
        return Binder(self)

    #to override
    def exit(self):
        print("exit() DOES NOTHING (should be overriden)")

    def _getAllJs(self) -> list:
        """ get a list of IIFE js declared script of this tag and its children"""
        ll=[]
        if self.js:
            logger.debug("Init Script (.js) found in %s --> '%s'",repr(self),self.js)
            ll.append( self._genIIFEScript( self.js ) ) #IIFE !

        def rec(childs:Sequence):
            for i in childs:
                if isinstance(i,Tag):
                    ll.extend( i._getAllJs() )
                elif isinstance(i,TagBase):
                    rec(i._childs)

        rec(self._childs)

        return ll

    def __call__(self, js:str):
        if self.hr is None:
            logger.error(f"call js is not possible, {repr(self)} is not tied to HRenderer !")
        else:
            self.hr._addInteractionScript( self._genIIFEScript(js) )

    def add(self,elt:AnyTags):
        """ override tagbase.add to feed 'tag._hr' with the hrenderer of the parent/self """
        if isinstance(elt,Tag):
            elt.hr = self.hr
            elt.parent = self
        elif not isinstance(elt,str) and hasattr(elt,"__iter__"):
            for i in elt:
                if isinstance(i,Tag):
                    i.hr = self.hr
                    i.parent = self
        TagBase.add(self,elt)

    def _genIIFEScript(self,js:str) -> str:
        return f"(function(tag){{ {js}\n }})(document.getElementById('{id(self)}'));"

    def _hasRender(self):
        if hasattr(self,"render"):
            render = getattr(self,"render")
            if callable(render):
                return render

    def __str__(self):
        render = self._hasRender()
        if render:
            logger.debug("Tag.__str__() : %s rendering itself with its render() method", repr(self))
            self.clear()
            render()
        else:
            logger.debug("Tag.__str__() : render str for %s", repr(self))
        return TagBase.__str__(self)


