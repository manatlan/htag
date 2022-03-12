# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2022 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/thag
# #############################################################################

# mono instance
from .browserstarlettehttp import BrowserStarletteHTTP
from .browserstarlettews import BrowserStarletteWS
from .browserhttp import BrowserHTTP
from .pywebview import PyWebWiew
from .guyapp import GuyApp

# multi instance
from .webhttp import WebHTTP

__all__ = ["BrowserHTTP","PyWebWiew","GuyApp","BrowserStarletteHTTP","BrowserStarletteWS","WebHTTP"]