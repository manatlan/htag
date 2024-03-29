# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

import json
import urllib.parse

def url2ak(url:str):
    """ transform the querystring of 'url' to (*args,**kargs)"""
    info = urllib.parse.urlsplit(url)
    args=[]
    kargs={}
    if info.query:
        items=info.query.split("&")
        first=lambda x: x[0]
        for i in items:
            if i:
                if "=" in i:
                    if i.endswith("="):
                        kargs[ i.split("=")[0] ] = None
                    else:
                        tt=list(urllib.parse.parse_qs(i).items())[0]
                        kargs[ tt[0] ] = first(tt[1])
                else:
                    tt=list(urllib.parse.parse_qs("x="+i).items())[0]
                    args.append( first(tt[1]) )
    return tuple(args), dict(kargs)

#----------------------------------------------
import re
def match(mpath,path):
    "return a dict of declared vars from mpath if found in path"
    mode={
        "str":  r"[^/]+",    # default
        "int":  r"\\d+",
        "path": r".+",
    }
    
    #TODO: float, uuid ... like https://www.starlette.io/routing/#path-parameters
    
    patterns=[
        (re.sub( r"{(\w[\w\d_]+)}" , r"(?P<\1>%s)" % mode["str"], mpath), lambda x: x),
        (re.sub( r"{(\w[\w\d_]+):str}" , r"(?P<\1>%s)" % mode["str"], mpath), lambda x: x),
        (re.sub( r"{(\w[\w\d_]+):int}" , r"(?P<\1>%s)" % mode["int"], mpath), lambda x: int(x)),
        (re.sub( r"{(\w[\w\d_]+):path}" , r"(?P<\1>%s)" % mode["path"], mpath), lambda x: x),
    ]
    
    dico={}
    for pattern,cast in patterns:
        g=re.match(pattern,path)
        if g:
            dico.update( {k:cast(v) for k,v in g.groupdict().items()} )
    return dico

#----------------------------------------------
import json,os
class SessionFile(dict):
    def __init__(self,file):
        self._file=file

        if os.path.isfile(self._file):
            with open(self._file,"r+") as fid:
                d=json.load(fid)
        else:
            d={}

        super().__init__( d )

    def __delitem__(self,k:str):
        super().__delitem__(k)
        self._save()

    def __setitem__(self,k:str,v):
        super().__setitem__(k,v)
        self._save()

    def clear(self):
        super().clear()
        self._save()

    def _save(self):
        if len(self):
            with open(self._file,"w+") as fid:
                json.dump(dict(self),fid, indent=4)
        else:
            if os.path.isfile(self._file):
                os.unlink(self._file)