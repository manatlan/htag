# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2024 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/htag
# #############################################################################
import sys
import types
import pytest

@pytest.fixture(autouse=True)
def cleanup_imports():
    """Fixture to ensure a clean slate for imports for each test."""
    original_modules = dict(sys.modules)

    # Unload modules that might interfere
    for mod in ['htag.ui', 'htagui', 'htagui.basics']:
        if mod in sys.modules:
            del sys.modules[mod]

    yield

    # Restore original modules
    sys.modules.clear()
    sys.modules.update(original_modules)


def test_ui_import_from_basics_jules():
    """ Test if 'htag.ui' imports from 'htagui.basics' when available """
    # Create fake modules
    htagui_module = types.ModuleType('htagui')
    basics_module = types.ModuleType('htagui.basics')
    basics_module.MyWidget = 'BasicsWidget'

    # Add to sys.modules
    sys.modules['htagui'] = htagui_module
    sys.modules['htagui.basics'] = basics_module

    # Import htag.ui and test
    import htag.ui
    assert hasattr(htag.ui, 'MyWidget')
    assert htag.ui.MyWidget == 'BasicsWidget'


def test_ui_import_fallback_to_htagui_jules():
    """ Test if 'htag.ui' falls back to importing from 'htagui' """
    # Create a fake htagui module (without .basics)
    htagui_module = types.ModuleType('htagui')
    htagui_module.MyWidget = 'HtaguiWidget'

    # Add to sys.modules
    sys.modules['htagui'] = htagui_module

    # Import htag.ui and test
    import htag.ui
    assert hasattr(htag.ui, 'MyWidget')
    assert htag.ui.MyWidget == 'HtaguiWidget'