# -*- coding: utf-8 -*-
# the simplest htag'app, in the best env to start development (hot reload/refresh)

from .tag import Tag

import json
import hashlib
md5= lambda x: hashlib.md5(x.encode('utf-8')).hexdigest()


###############################################################################
###############################################################################
import yaml,os
import shlex
import logging

logger = logging.getLogger(__name__)

class SyntaxError(Exception): pass  # pour les exceptions lies au format

class Fyt:
    """ this is a old bpm (doesn't have any clues with htag) """
    def __init__(self,scenarDef=None):
        if scenarDef is not None:
            if type(scenarDef) != dict:
                try:
                    if os.path.isfile(scenarDef):
                        scenarDef = yaml.load( open(scenarDef).read(), Loader=yaml.Loader )
                    elif isinstance(scenarDef,str):
                        scenarDef = yaml.load( scenarDef, Loader=yaml.Loader )
                    else:
                        raise SyntaxError("What's this scenarDef ?!")
                except Exception as e:
                    raise SyntaxError("Error %s" % e)

        self._defs=scenarDef
        self._level=[]


    def log(self,*z):
        logger.debug(("    " * (len(self._level)-1)) + " ".join(z))

    def run(self,entry,fix=lambda x:x ):
        """ retourne une structure arborescente des tests OK/KO """
        self.log(f"::: Run state '{entry}'")
        self.state["NODE"]=entry

        if entry not in self._defs: raise SyntaxError(f"Unknown state '{entry}' (not in {list(self._defs.keys())})")
        if self._defs[entry] is None: raise SyntaxError("Scenar vide ?!")

        def caller(method,a,k):
            signature="%s(%s)" % (
                ".".join(self._level + [method.__name__,]),
                ", ".join(["%s"%i for i in a] + ["%s=%s" % (x,y) for x,y in k.items()])
            )

            try:
                self.log( signature )
                rr=method(*a,**k)
                #~ if method==self.run:
                    #~ r[ a[0] ] = rr
            except TypeError as e:
                raise SyntaxError( "%s : %s" % (signature,e) )

        try:
            self._level.append( entry )
            for i in self._defs[entry]:
                try:
                    if type(i)==dict and len(i)==1: # [M] = appel method directe
                        # version dict (better way)
                        key,value=list(i.items())[0]
                        value = json.loads( json.dumps(value) ) # clone !IMPORTANT
                        method=getattr(self,key)
                        if type(value)==dict:
                            value={k:fix(v) for k,v in value.items()}
                            caller(method,(),value)
                        elif type(value)==list:
                            value=[fix(v) for v in value]
                            caller(method,tuple(value),{})
                        else:
                            value=fix(value)
                            caller(method,(value,),{})
                    elif isinstance(i,str):  # [S] = c un shortcut vers une methode
                        key,*args = list(shlex.split( i ))
                        method=getattr(self,key)
                        args=[fix(v) for v in args]
                        caller(method,tuple(args),{})
                    else:
                        raise SyntaxError(f"Strange command line {i}")
                except AttributeError as e:
                    raise SyntaxError(f"Unknow command : {e}")

        finally:
            self._level.pop()
###############################################################################
###############################################################################
###############################################################################



class BPM(Fyt):

    _instances = {} # to manage htag object for draw/redraw

    def __init__(self,state,scopes):
        if isinstance(scopes,dict):
            assert all([isinstance(k,str) and issubclass(v,Tag) for k,v in scopes.items()])
            self._scopes=scopes
        elif isinstance(scopes,list):
            assert all([issubclass(v,Tag) for v in scopes])
            self._scopes={i.__name__:i for i in scopes}

        self.state=state and state or {}
        Fyt.__init__(self,self.__doc__)

    def __call__(self, state, **params):
        """ the state runner """
        self.state.update( params ) # put the params into "states" !!!!!
        Fyt.run(self,state,fix=self._resolver)

    def _resolver(self,v):
        """ for substituing own vars (specific to HtagBPM) """
        if isinstance(v,str) and v.startswith("<") and v.endswith(">"):
            key = v[1:-1]
            if key in self.state:
                return self.state[ key ]
            else:
                raise SyntaxError(f"WTF {key} ?")
        else:
            return v


    def draw(self,oname) -> Tag:
        """ return the current htag instance of state var 'oname' """
        if oname in self.state:
            tup = self.state[oname]
            if type(tup)== tuple:
                tup_md5 = md5(str(tup))
                cur_tup_md5,cur_instance = self._instances.get(oname, (None,None) )
                if cur_tup_md5 == tup_md5:
                    self.log(f"--- Draw {oname} (REUSE {tup})")
                    instance = cur_instance
                else:
                    self.log(f"--- Draw {oname} (INSTANCIATE {tup})")
                    c,a,k = tup
                    if c in self._scopes:
                        instance = self._scopes[c](*a,**k)
                    else:
                        raise SyntaxError(f"Htag object '{c}' is not available in scopes")
                    self._instances[oname]=( tup_md5, instance )
                return instance

    # default keywords language :
    def call(self,state):
        self(state)

    def set(self,key,value):
        self.state[key]=value

    def redraw(self,key,className,*a,**k):
        if className in self._scopes:
            self.set( key, (className,a,k) )
        else:
            raise SyntaxError(f"Unknown className '{className}'")



if __name__ == "__main__":

    #########################################################################
    # test FYT
    #########################################################################
    class My(Fyt):
        d={}
        def run(self,entry,**data):
            self.d.update(data)
            Fyt.run(self,entry)

        def set(self,key,value):
            self.d[key]=value
        def test(self,condition,ok,ko=None):
            self.run( ok if eval(condition,{},self.d) else ko )
        def println(self,msg):
            print("RESULTAT:",msg)

    d="""

        devine:
            - set:
                key: nbToFound
                value: 41
            - test:
                condition: nb == nbToFound
                ok: same
                ko: notSame

        notSame:
            - test:
                condition: nb > nbToFound
                ok: tooBig
                ko: tooLittle

        same:
            - println "BRAVO"
            - set:
                key: nbToFound
                value: None

        tooBig:
            - println "C trop grand"

        tooLittle:
            - println "C trop petit"
    """

    N=My(d,False)

    N.run( "devine" , nb=12)
    N.run( "devine" , nb=46)
    N.run( "devine" , nb=41)

    print(N.d)  # <= dico
