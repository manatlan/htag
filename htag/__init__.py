# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################

from .tag import Tag,HTagException

try:
    import yaml
    from .bpm import BPM
except:
    class BPM:
        def __init__(self,*a,**k):
            raise Exception("BPM is available only if pyyaml is present ;-(")
            # at least, for this preversion (in future : i will find something)


__version__ = "0.0.0" # auto-updated

__all__= ["Tag","HTagException","BPM"]

