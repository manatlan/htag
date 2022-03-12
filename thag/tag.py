# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/thag
# #############################################################################
import html,json,hashlib

class ThagException(Exception): pass

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
    tag="div" # default one

    def __init__(self, content=None,**_attrs):
        if content is None:
            self._contents=[]
        elif type(content) in [list,tuple]:
            self._contents=list(content)
        else:
            self._contents=[content]


        self._attrs={}
        for k,v in _attrs.items():
            if not k.startswith("_"):
                raise ThagException(f"Can't set attribus without underscore ('{k}' should be '_{k}')") # for convention only ;-(
            else:
                self[ k[1:].replace("_","-") ] = v

        # compute a md5 (to indentify state for statics only now)
        self.md5 = md5( str(self._attrs) + str(self._contents))

    def __le__(self, o):
        self.add(o)
        return o

    def clear(self):
        self._contents=[]

    def add(self,elt):
        if type(elt) in [list,tuple]:
            for i in elt:
                self._contents.append(i)
        else:
            self._contents.append(elt)

    def __setitem__(self,attr,value):
        self._attrs[attr]=value
    def __getitem__(self,attr):
        return self._attrs.get(attr,None)

    def __str__(self):
        self._image=None

        rattrs=[]
        for k,v in self._attrs.items():
            if v is not None:
                if isinstance(v,bool):
                    if v == True:
                        rattrs.append(k)
                else:
                    rattrs.append( '%s="%s"' % (k,html.escape( str(v) )) )
        return """<%(tag)s%(attrs)s>%(content)s</%(tag)s>""" % dict(
            tag=self.tag.replace("_","-"),
            attrs=" ".join([""]+rattrs) if rattrs else "",
            content=" ".join([str(i) for i in self._contents if i is not None]),
        )

    def _getStateImage(self) -> str:
        """Return a str'image (state) of the object, for quick detection (see Stater())"""
        image=lambda x: "[%s]"%id(x) if isinstance(x,Tag) else str(x)
        return """<%(tag)s%(attrs)s>%(content)s</%(tag)s>""" % dict(
            tag=self.tag,
            attrs=str(self._attrs),
            content=" ".join([image(i) for i in self._contents]),
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}'{self.tag} {self._attrs} (childs:{len(self._contents)})>"

class TagCreator(type):
    def __getattr__(self,name:str):
        return type('TagBaseClone', (TagBase,), {**TagBase.__dict__,"tag":name})


class Binder:
    def __init__(self,btag_instance):
        self.__instance=btag_instance
    def __getattr__(self,method:str):
        m=hasattr(self.__instance,method) and getattr(self.__instance,method)
        if m and callable( m ):
            def _(*args,**kargs):
                return genJsInteraction(id(self.__instance),method,args,kargs)
            return _
        else:
            raise ThagException("Unknown method '%s' in '%s'"%(method,self.__instance.__class__.__name__))

class Tag(TagBase,metaclass=TagCreator): # custom tag (to inherit)
    statics = [] # list of "Tag", imported at start

    js=None  # post script, useful for js/init when tag is rendered

    def __init__(self, **_attrs):
        attrs={}
        auto={}
        for k,v in _attrs.items():
            if k.startswith("_"):
                attrs[k]=v
            else:
                auto[k]=v

        self.__dict__.update(auto)

        if "_id" in attrs:
            raise ThagException("can't set the html attribut '_id'")
        else:
            attrs["_id"]=id(self)   # force an @id !
        TagBase.__init__(self,None, **attrs)


    @property
    def bind(self):
        """ to bind method ! and return its js repr"""
        return Binder(self)

    #to override
    def exit(self):
        pass


    def _getAllJs(self) -> list:
        """ get a list of IIFE js declared script of this tag and its children"""
        ll=[]
        if self.js:
            ll.append( self._genIIFEScript( self.js ) ) #IIFE !

        for i in self._contents:
            if isinstance(i,Tag):
                ll.extend( i._getAllJs() )

        return ll

    def _genIIFEScript(self,js:str) -> str:
        return f"(function(tag){{ {js} }})(document.getElementById('{id(self)}'));"

    def _getTree(self) -> dict: #or None
        ll=[]

        for i in self._contents:
            if isinstance(i,Tag):
                ll.append( i._getTree() )

        return {self:ll}

