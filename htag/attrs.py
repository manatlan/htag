

class StrClass:
    """ mimic the js tag.classList """
    def __init__(self,txt=None):
        if txt is None:
            self._ll=[]
        else:
            if isinstance(txt,list):
                self._ll = list(txt)
            else:
                self._ll=[i.strip() for i in str(txt).split(" ") if i.strip()]

    def contains(self,c) -> int:
        return self._ll.count(c)

    def __contains__(self,kk):
        return self.contains(kk)>0

    def add(self,*cc):
        for c in cc:
            if not self.contains(c):
                self._ll.append(c)

    def remove(self,*cc):
        for c in cc:
            if self.contains(c):
                self._ll.remove(c)

    def toggle(self,c):
        if c in self._ll:
            self.remove(c)
        else:
            self.add(c)

    @property
    def list(self)-> list:
        """ return the python's list, to access more python list methods ;-) """
        return self._ll

    def __add__(self,t:str):
        return StrClass(str(self) + t)
    def __radd__(self,t:str):
        return StrClass(t + str(self))

    def __eq__(self,x):
        return str(self)==str(x)

    def __len__(self):
        return len(self._ll)

    def __str__(self):
        return " ".join(self._ll)
    def __repr__(self):
        return " ".join(self._ll)

#---------------------------------------------------------------

keyize = lambda x: x.strip().lower()


class DictStyle(dict):
    def __init__(self,parent):
        self._parent = parent
        dict.__init__(self,self._parent._ll)

    def __setitem__(self, k, v) -> None:
        self._parent.set(k,v,True)

    def clear(self) -> None:
        self._parent._ll=[]

    def update(self, d:dict):
        for k,v in d.items():
            self[k]=v

class StrStyle:
    """ expose basic methods set/get/contains/remove """
    def __init__(self,txt=None):
        self._ll=[]
        if txt is not None:
            if isinstance(txt,dict):
                self._ll = list(txt.items())
            else:
                for i in str(txt).split(";"):
                    if i and ":" in i:
                        k,v=i.strip().split(":",1)
                        self._ll.append( (keyize(k),v.strip()) )
    @property
    def dict(self):
        """ return a python's dict, to access more python dict methods ;-) """
        return DictStyle(self)

    def set(self,k,v,unique=False):
        if unique: self.remove(k)
        self._ll.append( (keyize(k),v.strip()) )

    def get(self,kk) -> list:
        return [v for k,v in self._ll if keyize(kk)==k]

    def contains(self,kk) -> int:
        return len(self.get(kk))

    def __contains__(self,kk):
        return self.contains(kk)>0

    def remove(self,kk) -> bool:
        ll=[(k,v) for k,v in self._ll if keyize(kk)==k]
        for i in ll:
            self._ll.remove(i)
        return len(self._ll)>0

    def __add__(self,t:str):
        assert ":" in t
        return StrStyle(str(self) + t)
    def __radd__(self,  t:str):
        assert ":" in t
        return StrStyle(t + str(self))

    def __eq__(self,x):
        return str(self)==str(x)

    def __len__(self):
        return len(self._ll)

    def __str__(self):
        return "".join(["%s:%s;" %(k,v) for k,v in self._ll])
    def __repr__(self):
        return "".join(["%s:%s;" %(k,v) for k,v in self._ll])

