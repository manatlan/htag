# -*- coding: utf-8 -*-
# # #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/thag
# #############################################################################

from .tag import Tag,ThagException

__version__ = "0.0.2" # updated from pypoetry.toml

__all__= ["Tag","ThagException"]

def _majVersion():
    """ called by build script (to update __version__ from toml)
        "python3 -c 'from thag import _majVersion; _majVersion()"
     """
    import re,tomlkit

    file='thag/__init__.py'
    content = open(file,'r+').read()
    v=tomlkit.parse(open('pyproject.toml').read())['tool']['poetry']['version']
    with open(file,'w+') as fid:
        fid.write( re.sub(r'__version__ = "[^"]+"','__version__ = "%s"'%v,content,1) )
    print("thag.__version__ UPDATED to '%s'"%v)