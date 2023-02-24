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
import time

class HRSessions:
    def __init__(self):
        self._data={}

    def set_hr(self,fqn:str,hr:type):
        """ save the hrenderer for fqn"""
        self._data[fqn]=dict(lastaccess=time.time(),hrenderer=hr)

    def get_hr(self,fqn:str): # -> HRenderer
        """ get the hrenderer for fqn or None"""
        info=self._data.get(fqn)
        if info:
            info["lastaccess"]=time.time()
            return info["hrenderer"]

