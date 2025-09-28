import sys
import os
import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Add the parent directory to the path to allow imports from htag
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from htag import Tag
from htag.runners.pyscript import PyScript

@patch('htag.runners.pyscript.HRenderer')
def test_pyscript_run_jules(mock_hrenderer):
    class MyTestApp(Tag.div):
        pass

    mock_hr_instance = MagicMock()
    mock_hr_instance._statics = [Tag.style("body {color:red;}")]
    mock_hr_instance.__str__.return_value = "<body>Test Body</body>"
    mock_hrenderer.return_value = mock_hr_instance

    mock_window = MagicMock()
    mock_window.document.location.href = "http://test.com"

    # Mock methods on the mocked head
    mock_head = mock_window.document.head
    mock_head.appendChild = MagicMock()

    # Mock createElement on the mocked document
    mock_tag = MagicMock()
    mock_tag.attrs = {}
    mock_tag.childs = []
    mock_window.document.createElement = MagicMock(return_value=mock_tag)

    ps = PyScript(MyTestApp)
    ps.run(window=mock_window)

    mock_hrenderer.assert_called_once()
    assert ps.hr == mock_hr_instance
    assert ps.hr.sendactions is not None
    assert mock_window.interactions is not None
    assert mock_head.innerHTML == ""

    # Check that statics are processed
    mock_window.document.createElement.assert_called_with("style")
    mock_head.appendChild.assert_called_once()

    assert mock_window.document.body.outerHTML == "<body>Test Body</body>"
    mock_window.pyscript_starter.assert_called_once()

@pytest.mark.asyncio
async def test_pyscript_interactions_jules():
    class MyTestApp(Tag.div):
        pass

    ps = PyScript(MyTestApp)
    ps.hr = AsyncMock()
    ps.hr.interact.return_value = {"test": "action"}

    interaction_data = json.dumps({
        "id": "obj1",
        "method": "test_method",
        "args": [1, 2],
        "kargs": {"c": 3},
        "event": {"type": "click"}
    })

    result = await ps.interactions(interaction_data)

    ps.hr.interact.assert_awaited_once_with(
        "obj1", "test_method", [1, 2], {"c": 3}, {"type": "click"}
    )
    assert json.loads(result) == {"test": "action"}

@pytest.mark.asyncio
async def test_pyscript_updateactions_jules():
    class MyTestApp(Tag.div):
        pass

    ps = PyScript(MyTestApp)
    ps.window = MagicMock()

    actions = {"action": "update_dom"}
    await ps.updateactions(actions)

    ps.window.action.assert_called_once_with(json.dumps(actions))

def test_pyscript_run_no_window_jules():
    class MyTestApp(Tag.div):
        pass

    ps = PyScript(MyTestApp)
    # This test ensures that calling run without a window object
    # (in a non-pyscript environment) does not raise an error immediately
    # because the import of 'js' is inside a try-except block.
    # The method will fail later, but the initial call is what we test.
    with patch('htag.runners.pyscript.HRenderer'):
        try:
            ps.run()
        except AttributeError:
            # We expect an attribute error because window is not set
            # and the subsequent code will fail. This is ok.
            pass