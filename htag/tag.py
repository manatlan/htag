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
logger = logging.getLogger(__name__)

class HTagException(Exception): pass

md5= lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()

def stringify(obj):
    def my(obj):
        if isinstance(obj,bytes): # trick to convert b'' -> pure javascript
            return "<:<:%s:>:>" % obj.decode()
    return json.dumps(obj, default=my).replace('"<:<:',"").replace(':>:>"',"")

def genJsInteraction(id,method=None,args=None,kargs=None):
    interact=dict(id=id,method=method,args=args,kargs=kargs)
    return f"""interact( {stringify(interact)} );"""


class TagBase:
    """ This is a class helper to produce a "HTML TAG" """
    tag: str="div" # default one

    def __init__(self, content=None,**_attrs):
        self.set(content)

        self._attrs={}
        for k,v in _attrs.items():
            if not k.startswith("_"):
                raise HTagException(f"Can't set attributs without underscore ('{k}' should be '_{k}')") # for convention only ;-(
            else:
                self[ k[1:].replace("_","-") ] = v

        # compute a md5 (to indentify state for statics only now)
        # WARN : attrs or content change -> doesn't affect md5 !
        self.md5 = md5( str(self._attrs) + str(self._contents))

    def __le__(self, o):
        self.add(o)
        return o

    def clear(self):
        self._contents=[]

    def set(self,elt):
        """ a bit like .innerHTML setting (avoid clear+add)"""
        self.clear()
        self.add( elt)

    def add(self,elt):
        """ add an object or a list/tuple of objects """
        if elt is None:
            pass
        elif not isinstance(elt,str) and hasattr(elt,"__iter__"):
            for i in elt:
                self._contents.append(i)
        else:
            self._contents.append(elt)

    def __setitem__(self,attr,value):
        self._attrs[attr]=value
    def __getitem__(self,attr):
        return self._attrs.get(attr,None)

    def __str__(self):
        return self.__render__( self._attrs.items() , str )

    def _renderStatic(self):
        """ IT REMOVES @ID on tagbase too ;-( """
        mystr = lambda x: x._renderStatic() if isinstance(x,TagBase) else str(x)
        attrs = [(k,v) for k,v in self._attrs.items() if k != "id" ]
        return self.__render__(attrs,mystr)

    def __render__(self, attrs, mystr ):
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
            content="".join([mystr(i) for i in self._contents if i is not None]),
        )



    def _getStateImage(self) -> str: #TODO: could disapear (can make something more inteligent here!)
        """Return a str'image (state) of the object, for quick detection (see Stater())"""

        logger.debug("Force Tag rendering (for state image): %s",repr(self))
        str(self) # force a re-rendering (for builded lately)

        image=lambda x: "[%s]"%id(x) if isinstance(x,Tag) else str(x)
        return """%s%s:%s""" % (
            self.tag,
            self._attrs,
            [image(i) for i in self._contents],
        )

    def _getTree(self) -> dict:
        """ return a tree of TagBase childs """
        ll=[]

        for i in self._contents:
            if isinstance(i,TagBase):
                ll.append( i._getTree() )

        return {self:ll}

    def __repr__(self):
        return f"<{self.__class__.__name__}'{self.tag} {self._attrs.get('id')} (childs:{len(self._contents)})>"




class TagBaseCreator(type):
    def __getattr__(self,name:str):
        return type('TagBase%s' % name.capitalize(), (TagBase,), {**TagBase.__dict__,"tag":name})

class H(metaclass=TagBaseCreator): # Html
    def __init__(self):
        raise HTagException("no!")


class TagCreator(type):
    def __getattr__(self,name:str):
        if name == "H":
            return H
        else:
            return type('Tag%s' % name.capitalize(), (Tag,), {**Tag.__dict__,"tag":name})

class Caller:
    def __init__(self,instance, callback, args, kargs):
        self.instance = instance
        self.callback = callback
        self.args = args
        self.kargs = kargs
        
        self._others=[]
        self._assigned = None
    
    def bind(self,callback,*args,**kargs): # -> Caller
        if any( [isinstance(i,bytes) for i in args] ) or any( [isinstance(i,bytes) for k,i in kargs.items()] ):
            raise HTagException("Can't bind (bytes)'js_arg' in next binders !")
        self._others.append( (callback,args,kargs) )
        return self

    def assignEventOnTag(self, object, event):
        self._assigned = "%s-%s" % (event,id(object)) # unique identifier for the event 'event' of the tag 'object'
        self.instance._callbacks_[self._assigned]=self   # save the Caller in _callbacks_ of self.instance
        return self

    def __str__(self) -> str:
        if not self._assigned: 
            raise HTagException("Caller can't be serizalized, it's not _assign'ed to an event !")
        return self.instance.bind.__on__(self._assigned,*self.args,**self.kargs)

class Binder:
    def __init__(self,btag_instance):
        self.__instance=btag_instance
    def __getattr__(self,method:str):
        m=hasattr(self.__instance,method) and getattr(self.__instance,method)
        if m and callable( m ):
            def _(*args,**kargs) -> str:
                return genJsInteraction(id(self.__instance),method,args,kargs)
            return _
        else:
            raise HTagException("Unknown method '%s' in '%s'"%(method,self.__instance.__class__.__name__))

    def __call__(self,callback,*args,**kargs) -> Caller:
        return Caller(self.__instance,callback,args,kargs)


class Tag(TagBase,metaclass=TagCreator): # custom tag (to inherit)
    statics: list = [] # list of "Tag", imported at start

    __instances__ = weakref.WeakValueDictionary()

    js: str = None  # post script, useful for js/init when tag is rendered

    @classmethod
    def NoRender(cls,f):
        f._norender = True
        return f

    @classmethod
    def find_tag(cls, obj_id):
        return cls.__instances__.get(obj_id, None)

    def __init__(self, content=None,**_attrs):
        self._callbacks_={}
        attrs={}
        auto={}
        for k,v in _attrs.items():
            if k.startswith("_"):
                attrs[k]=v
            else:
                auto[k]=v

        self.__dict__.update(auto)

        if "_id" in attrs:
            raise HTagException("can't set the html attribut '_id'")
        else:
            attrs["_id"]=id(self)   # force an @id !
        TagBase.__init__(self,None, **attrs)
        self.set(content)
        Tag.__instances__[id(self)]=self

    # new mechanism (could replace self.bind.<m>()) ... one day
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

    async def __on__(self,eventjs,*a,**ka):
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

    def __setitem__(self,attr,value):
        if type(value) in [types.FunctionType,types.MethodType]:
            value = Caller( self, value, (), {})
            value.assignEventOnTag( self, attr )
            logger.info("Assign event '%s' (simple callback) on %s" % (attr,repr(self)))
        elif isinstance(value,Caller):
            value.assignEventOnTag( self, attr )
            logger.info("Assign event '%s' (handled) on %s" % (attr,repr(value.instance)))
        else:
            newvalue = value
        TagBase.__setitem__(self,attr,value)
    #-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


    @property
    def bind(self):
        """ to bind method ! and return its js repr"""
        return Binder(self)

    #to override
    def exit(self):
        print("exit() DOES NOTHING (should be overrided)")

    def _getAllJs(self) -> list:
        """ get a list of IIFE js declared script of this tag and its children"""
        ll=[]
        if self.js:
            logger.debug("Init Script (.js) found in %s --> '%s'",repr(self),self.js)
            ll.append( self._genIIFEScript( self.js ) ) #IIFE !

        def rec(childs):
            for i in childs:
                if isinstance(i,Tag):
                    ll.extend( i._getAllJs() )
                elif isinstance(i,TagBase):
                    rec(i._contents)

        rec(self._contents)

        return ll

    def _genIIFEScript(self,js:str) -> str:
        return f"(function(tag){{ {js}\n }})(document.getElementById('{id(self)}'));"

    def __str__(self):
        logger.debug("Tag.__str__() : render str for %s", repr(self))
        return TagBase.__str__(self)


