import pytest
import json
from unittest.mock import MagicMock, AsyncMock
from htag.server import Event, AppRunner as App
from htag import Tag

@pytest.mark.asyncio
async def test_event_simple_value():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "custom",
        "data": "hello"
    }
    e = Event(target, msg)
    assert e.value == "hello"

@pytest.mark.asyncio
async def test_event_hashchange_data():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "hashchange",
        "data": {
            "newURL": "http://localhost/#new",
            "oldURL": "http://localhost/#old",
            "callback_id": "123"
        }
    }
    e = Event(target, msg)
    assert e.newURL == "http://localhost/#new"
    assert e.oldURL == "http://localhost/#old"

@pytest.mark.asyncio
async def test_app_handle_simple_event():
    app = App()
    shared = {"val": None}
    
    def my_cb(e):
        shared["val"] = e.value
        
    # We simulate a tag that has a custom event handler
    class MyTag(Tag.div):
        def init(self):
            self._oncustom = my_cb
            
    tag = MyTag()
    app += tag
    
    ws = AsyncMock()
    msg = {
        "id": tag.id,
        "event": "custom",
        "data": "simple_value"
    }
    
    await app.handle_event(msg, ws)
    assert shared["val"] == "simple_value"

@pytest.mark.asyncio
async def test_app_handle_hashchange_event():
    app = App()
    shared = {"new": None, "old": None}
    
    def on_hash(e):
        shared["new"] = e.newURL
        shared["old"] = e.oldURL
        
    app._onhashchange = on_hash
    
    ws = AsyncMock()
    msg = {
        "id": app.id,
        "event": "hashchange",
        "data": {
            "newURL": "new_url",
            "oldURL": "old_url"
        }
    }
    
    await app.handle_event(msg, ws)
    assert shared["new"] == "new_url"
    assert shared["old"] == "old_url"
