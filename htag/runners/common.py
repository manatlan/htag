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

class Sessions(dict):
    def __init__(self):
        dict.__init__(self,{})

    def get_ses(self,htuid):
        """ return the underlying session dict for this htuid """
        assert htuid is not None
        if htuid not in self.keys():
            # create a empty "data_ses"
            self[htuid] = dict(apps={},session={})

        return self[htuid]
    
    def set_hr(self,sesid:str,hr:type):
        """ save the hrenderer for sesid"""
        fqn,htuid = sesid.split("|")
        data_ses=self.get_ses(htuid)
        data_app=data_ses["apps"].setdefault( fqn , {})
        data_app["lastaccess"]=time.time()
        data_app["hrenderer"]=hr

    def get_hr(self,sesid:str): # -> HRenderer
        """ get the hrenderer for sesid or None"""
        fqn,htuid = sesid.split("|")  
        data_ses = self.get_ses(htuid)
        
        data_app=data_ses["apps"].get( fqn )
        if data_app:
            data_app["lastaccess"]=time.time()
            return data_app["hrenderer"]
    
    def del_hr(self,sesid:str) -> bool:
        """ delete the sesid """
        fqn,htuid = sesid.split("|")  
        try:
            del self[ htuid ]["apps"][ fqn ]
            return True
        except:
            return False
    
    def purge(self,timeout) -> int:
        """ remove apps from session whose are older than 'timeout' seconds"""
        now=time.time()
        to_remove=[]
        for htuid,data_ses in self.items():
            for fqn,data_app in data_ses.get("apps",{}).items():
                if now - data_app["lastaccess"] > timeout:
                    to_remove.append( (htuid,fqn) )
        for htuid,fqn in to_remove:
            self.del_hr( fqn+"|"+htuid )
        return len(to_remove)


    @property
    def htuids(self):
        return list(self.keys())

    @property
    def sesids(self):
        ll=[]
        for htuid,data_ses in self.items():
            for fqn,data_app in data_ses.get("apps",{}).items():
                    ll.append( (htuid,fqn) )
        return [ f"{fqn}|{htuid}" for htuid,fqn in ll]

    def __str__(self):
        def my(obj):
            if isinstance(obj,type):
                return "<"+obj.__class__.__name__+">"
        return json.dumps(self, default=my, indent=4)
