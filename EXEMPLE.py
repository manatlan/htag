#!/usr/bin/python
# -*- coding: utf-8 -*-

from htag import Tag

class Ya(Tag.div):
    statics = Tag.H.style("""body {font-size:100px}""", _id="Ya")
    
    def __init__(self):
        super().__init__()
        self <= "Ya"


class Yo(Tag.div):
    statics = Tag.H.style("""body {background:#CFC;}""", _id="Yo")
    
    def __init__(self):
        super().__init__()
        self <= "Yo"


class App(Tag.body):
    statics = Tag.H.style("""body {color: #080}""", _id="main")
    imports = Yo
    
    def __init__(self):
        super().__init__()
        
        self <= Yo()
        

if __name__=="__main__":
    from htag.runners.browserhttp import HRenderer
    import re
    
    html=str(HRenderer( App(), ""))
    styles = re.findall("(<style[^<]+</style>)",html)
    assert len(styles)==2
    quit()
    
