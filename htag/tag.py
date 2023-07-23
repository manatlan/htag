# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################
import html,json
import hashlib
import logging,types,asyncio
import weakref
import inspect
from typing import Sequence,Union,Optional,Any,Callable,Type
from .attrs import StrClass,StrStyle

md5= lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()

AnyTags = Union[ Optional[Any], Sequence[Any]]
StrNonable = Optional[str]

logger = logging.getLogger(__name__)

class HTagException(Exception): pass

#md5= lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()

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
    def __str__(self):
        return "".join([str(i) for i in self])

    def __repr__(self):
        return f"<Elements {list(self)}>"




class NotBindedCaller:
    def __init__(self,instance,on_event):
        self.__event = on_event
        self.__instance=instance
        self._befores=[]
        self._afters=[]

    def __add__(self,js:str): # -> X Caller
        if not isinstance(js,str):
            raise HTagException("Can't add non string to a Caller")
        self._afters.append(js)
        return self

    def __radd__(self,js:str): # -> X Caller
        if not isinstance(js,str):
            raise HTagException("Can't radd non string to a Caller")
        self._befores.append(js)
        return self

    def bind(self,callback:Callable,*args,**kargs): #-> Caller
        c = Caller(self.__instance,callback,args,kargs)
        c.assignEventOnTag( self, self.__event  )
        self.__instance[self.__event]=c
        return c

    def __str__(self):
        return ";".join(self._befores+self._afters)


class Caller(NotBindedCaller):
    def __init__(self,instance, callback:Callable, args:tuple, kargs:dict):
        super().__init__(instance,None)
        if not callable(callback): raise HTagException("The caller must be callable !")
        self.instance = instance
        self.callback = callback
        self.args = args
        self.kargs = kargs

        self._others=[]
        self._assigned = None

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


    def __call__(self):
        self.callback( self.instance )

    def __str__(self) -> str:
        if not self._assigned:
            raise HTagException("Caller can't be serizalized, it's not _assign'ed to an event !")
        newargs = tuple([self._assigned]+list(self.args))
        bc=BaseCaller(self.instance,"__on__", newargs, self.kargs)
        bc._befores = self._befores
        bc._afters = self._afters
        return str(bc)

class BaseCaller(NotBindedCaller):
    def __init__(self,instance, mname:StrNonable=None, args=None, kargs=None):
        super().__init__(instance, None)

        self.instance = instance
        self.mname = mname
        self.args = args
        self.kargs = kargs

    def __str__(self) -> str:
        interact=dict(id=id(self.instance),method=self.mname,args=self.args,kargs=self.kargs,event=b"jevent(event)")
        gen = lambda ll: (";".join(ll))+";" if ll else ""
        return f"""try{{{gen(self._befores)}interact( {stringify(interact)} );{gen(self._afters)}}} catch(e) {{_error(e,"JS")}}"""

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


class InternalCall:
    def __init__(self,btag_instance):
        self.__instance=btag_instance

    def __getattr__(self,method:str):
        m=hasattr(self.__instance,method) and getattr(self.__instance,method)
        if m and callable( m ):
            def _(*args,**kargs) -> None:
                self.__call__( getattr(self.__instance.bind, method )(*args,**kargs) )
            return _
        else:
            raise HTagException("Unknown method '%s' in '%s'"%(method,self.__instance.__class__.__name__))

    def __call__(self,js:str) -> None:
        """ Send "js to execute" (post js) now """
        if self.__instance.root is None or self.__instance.root._hr is None:
            raise HTagException("call js is not possible, %s is not tied to a parent/HRenderer !", repr(self.__instance))
        else:
            self.__instance.root._hr._addInteractionScript( self.__instance._genIIFEScript(js) )



class TagCreator(type):
    def __getattr__(self,name:str) -> Type:
        return type('Tag%s' % name.capitalize(), (Tag,), {**Tag.__dict__,"tag":name})

class Tag(metaclass=TagCreator): # custom tag (to inherit)

    #======================================================================
    # statics
    #======================================================================
    statics: list = [] # list of "Tag", imported at start in html>head
    imports = None

    __instances__ = weakref.WeakValueDictionary()

    @classmethod
    def find_tag(cls, obj_id:int):
        return cls.__instances__.get(obj_id, None)


    #======================================================================
    # instance
    #======================================================================
    tag: StrNonable = None # default one
    js: StrNonable = None  # js script that is executed at each tag rendering
    STRICT_MODE:bool=False

    @property
    def bind(self):
        """ to bind method ! and return its js repr"""

        if self.tag is None:
            raise HTagException("This tag is a placeholder, it can't manage html attributs")

        return Binder(self)


    @property
    def call(self):
        """ to easyly call an own (self.) method
        TO AVOID : self.call( self.bind.mymethod(*a,**k) ) -> self.call.method(*a,**k)
        """

        if self.tag is None:
            raise HTagException("This tag is a placeholder, it can't call own methods directly ")

        return InternalCall(self)


    @property
    def childs(self) -> tuple:
        return tuple(self._childs)

    @property
    def attrs(self) -> dict:

        if self.tag is None:
            raise HTagException("This tag is a placeholder, it can't manage html attributs")

        return self._attrs

    @property
    def innerHTML(self) -> str:
        return "".join([str(i) for i in self._childs if i is not None])

    @property
    def root(self) -> "Tag":
        root= self
        while root.parent is not None:
            root = root.parent
        return root

    @property
    def parent(self):
        return self._parent


    @property
    def event(self) -> dict:
        return self._event


    #======================================================================
    # Constructor
    #======================================================================
    def __init__(self, *args,_hr_=None,**kargs):
        self._event={}       # NEW !!!!
        self._hr=_hr_           # the hrenderer instance
        self.session = _hr_.session if _hr_ else None
        self._parent=None
        self._callbacks_={}
        self._childs=Elements()
        self._attrs={}
        self._hash_=None

        # sorts kargs -> selfs/attrs
        attrs={}
        selfs={}
        for k,v in kargs.items():
            if k.startswith("_"):
                attrs[k]=v
            else:
                if k!="js" and k in dir(self)+["render"]:
                    raise HTagException(f"Can't autoset property '{k}' in '{repr(self)}', private property !")
                selfs[k]=v

        # own a simplified init() ?
        if hasattr(self,"init"):
            init = getattr(self,"init")
            init = init if callable(init) else None

            self.__declareArgsKargs(None,**attrs)

            if init: init(*args,**kargs)
            self.__dict__.update(selfs)
        else:
            # if no own 'init' method, declare default args (selfs) as attributs instance
            self.__dict__.update(selfs)

            self.__declareArgsKargs(*args, **attrs)

        # save the weakref to the tag, for Tag.find_tag(id) method
        Tag.__instances__[id(self)]=self

        # compute an hash at creation time (used in hrender to identify doubles)
        self._hash_ = md5( str(self._attrs.items())+str(self.childs) )

    def __declareArgsKargs(self, content:AnyTags=None,**_attrs):
        self.set(content)

        for k,v in _attrs.items():
            if k.startswith("_"):
                self[ k[1:].replace("_","-") ] = v
            else:
                raise HTagException(f"Can't set attributs without underscore ('{k}' should be '_{k}')") # for convention only ;-( (not possible to get it)

    #======================================================================
    # public methods
    #======================================================================
    async def update(self) -> bool:
        """ return True if component can update itself (ex: runner with ws)"""
        if self.root and self.root._hr:
            return await self.root._hr.update(self)
        else:
            logger.error("This component is not tied in a hrenderer")
            return false
            
    def clear(self):
        """ remove all childs """
        for t in self._childs:      # remove parenting
            if isinstance(t,Tag):
                t.remove()
        self._childs=Elements()

    def set(self,elt:AnyTags):
        """ a bit like .innerHTML setting (avoid clear+add)"""
        self.clear()
        self.add( elt)

    def remove(self, elt=None):
        """Remove an object(elt) from its childs, or itself (if none), if attached (has parent)"""
        if elt is None:
            if self._parent:
                return self._parent.remove(self)
        else:
            if elt in self._childs:
                self._childs.remove(elt)
                if isinstance(elt,Tag):
                    elt._parent=None #remove parenting
                return True

    def exit(self):
        """ method to override, for your own exit"""
        print("exit() DOES NOTHING (should be overriden)")

    def add(self, elt:AnyTags, reparent=False):
        """ add a element to this tag
        """
        if elt is not None:
            if isinstance(elt,Tag):
                if self.root.STRICT_MODE:
                    if (not reparent) and (elt.parent is not None):
                        raise HTagException(f"Can't add {repr(elt)} to {repr(self)} childs, it's already parented !")
                elt._parent = self
                self._childs.__add__(elt)
            elif not isinstance(elt,str) and hasattr(elt,"__iter__"):
                for i in list(elt):
                    self.add( i )
            else:
                self._childs.__add__(elt)

    #===============================================================================
    # Overriden methods
    #===============================================================================
    async def __on__(self,eventjs:str,*a,**ka):
        """ new mechanism (could replace self.bind.<m>()) ... one day"""
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


    def __getitem__(self,attr:str) -> Any:

        if self.tag is None:
            raise HTagException("This tag is a placeholder, it can't manage html attributs")

        attr=attr.strip().lower()
        r=self._attrs.get(attr,None)
        if r is None:
            if attr.startswith("on"):
                r = NotBindedCaller(self,attr)
            elif attr == "style":
                self._attrs["style"]=StrStyle()
                r = self._attrs["style"]
            elif attr == "class":
                self._attrs["class"]=StrClass()
                r = self._attrs["class"]
        return r


    def __setitem__(self,attr:str,value):

        if self.tag is None:
            raise HTagException("This tag is a placeholder, it can't manage html attributs")

        attr=attr.strip().lower()
        if type(value) in [types.FunctionType,types.MethodType]:
            value = Caller( self, value, (), {})
            value.assignEventOnTag( self, attr )
            logger.info("Assign event '%s' (simple callback) on %s" % (attr,repr(self)))
        elif isinstance(value,Caller):
            value.assignEventOnTag( self, attr )
            logger.info("Assign event '%s' (handled) on %s" % (attr,repr(value.instance)))

        if attr == "style":
            self._attrs["style"]=StrStyle(value)
        elif attr.strip().lower() == "class":
            self._attrs["class"]=StrClass(value)
        else:
            self._attrs[attr]=value

    def __le__(self, elt: AnyTags ):
        self.add(elt)
        return elt

    def __iadd__(self,  elt: AnyTags):
        ''' use "+=" instead of "<=" !!!! '''
        self.add(elt)
        return self

    def __add__(self,  elt):
        return Elements([self]) + elt
    def __radd__(self,  elt):
        return elt + Elements([self])

    def __repr__(self):
        if self.tag is None:
            return f"<{self.__class__.__name__}'PLACEHOLDER {id(self)} (childs:{len(self._childs)})>"
        else:
            return f"<{self.__class__.__name__}'{self.tag} {id(self)} (childs:{len(self._childs)})>"

    # DEPRECATED
    def __call__(self, js:str):
        msg = f"self( js ) is DEPRECATED, use self.call( js ) on {repr(self)}"
        logger.warning(msg)
        print("WARNING",msg)
        self.call(js)

    def __str__(self):
        render = self._hasARenderMethod()
        if render:
            logger.debug("Tag.__str__() : %s rendering itself with its render() method", repr(self))
            self.clear()
            render()
        else:
            logger.debug("Tag.__str__() : render str for %s", repr(self))

        needIds = self.root._hr is not None

        if self.tag is None:
            return "".join([str(i) for i in self._childs if i is not None])
        else:
            # fix attrs, depending on hr
            attrs = dict(self._attrs) # make a copy
            if needIds:
                if attrs.get("id"):
                    logger.warn("!!! **WARNING** Tag %s had an @id=%s, it was replaced for HRenderer needs !!!", repr(self),attrs["id"])
                attrs["id"]=id(self)

            # rewrite attrs(dict) -> nattrs(list)
            rattrs=[]
            for k,v in attrs.items():
                if v is not None:
                    if isinstance(v,bool):
                        if v == True:
                            rattrs.append(k)
                    else:
                        if v!="":
                            rattrs.append( '%s="%s"' % (k,html.escape( str(v) )) )

            return """<%(tag)s%(attrs)s>%(content)s</%(tag)s>""" % dict(
                tag=self.tag.replace("_","-"),
                attrs=" ".join([""]+rattrs) if rattrs else "",
                content="".join([str(i) for i in self._childs if i is not None]),
            )





    #===============================================================================
    # privates methods
    #===============================================================================
    def _getStateImage(self) -> str:
        """Return a str'image (state) of the object, for quick detection (see Stater())
           (btw child tags are represented by its id, to help Stater.guess for detection)
        """
        render = self._hasARenderMethod()
        if render: # force a re-rendering (for builded lately)
            logger.debug("Tag._getStateImage() : %s rendering itself with its render() method", repr(self))
            self.clear()
            render()

        image=lambda x: "[%s]"%id(x) if isinstance(x,Tag) else str(x)
        return """%s%s:%s""" % (
            self.tag,
            self._attrs,
            [image(i) for i in self._childs],
        )

    def _getTree(self) -> dict:
        """ return a tree of Tag childs """
        ll=[]

        for i in self._childs:
            if isinstance(i,Tag):
                ll.append( i._getTree() )

        return {self:ll}

    def _getAllJs(self) -> list:
        """ get a list of IIFE js declared script of this tag and its children"""
        ll=[]
        if self.js:
            logger.debug("Init Script (.js) found in %s --> '%s'",repr(self),self.js)
            ll.append( self._genIIFEScript( self.js ) ) #IIFE !

        for i in self._childs:
            if isinstance(i,Tag):
                ll.extend( i._getAllJs() )

        return ll

    def _genIIFEScript(self,js:str) -> str:
        """ genereate an IIFE wicth script 'js' whereas tag (deprecated), or self (the newest), is the js/node of the current object.
            (the goal is to have a quick reference to the node on js_side, ex: tag.js="self.focus()")
            ('tag' is now deprecated in favor of 'self' on versions > 0.9.13)
        """
        return f"(function(self,tag=self){{ {js}\n }})(document.getElementById('{id(self)}'));"

    def _hasARenderMethod(self) -> Union[ None, Callable]:
        if hasattr(self,"render"):
            render = getattr(self,"render")
            if callable(render):
                return render

