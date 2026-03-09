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

@pytest.mark.asyncio
async def test_event_dict_value():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "submit",
        "data": {
            "name": "manatlan",
            "age": 42
        }
    }
    e = Event(target, msg)
    # Standard htag v2: data is in .value
    assert e.value == {"name": "manatlan", "age": 42}
    # Backward compatibility / Convenience: subscriptable access
    assert e["name"] == "manatlan"
    assert e["age"] == 42
    assert e["missing"] is None

@pytest.mark.asyncio
async def test_event_getitem_fallback_to_attr():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "click",
        "data": {
            "pageX": 100,
            "pageY": 200
        }
    }
    e = Event(target, msg)
    # Should find in attributes (Event sets attrs from msg['data'])
    assert e["pageX"] == 100
    assert e.pageX == 100
    # Should work via __getitem__ too
    assert e["id"] == "123"

@pytest.mark.asyncio
async def test_app_handle_form_event():
    app = App()
    shared = {"data": None}
    
    def on_submit(e):
        shared["data"] = e.value
        
    class MyForm(Tag.form):
        def init(self):
            self._onsubmit = on_submit
            
    tag = MyForm()
    app += tag
    
    ws = AsyncMock()
    msg = {
        "id": tag.id,
        "event": "submit",
        "data": {
            "value": {"field1": "val1", "field2": "val2"}
        }
    }
    
    await app.handle_event(msg, ws)
    assert shared["data"] == {"field1": "val1", "field2": "val2"}

@pytest.mark.asyncio
async def test_event_priority_collision():
    target = MagicMock()
    msg = {
        "id": "real_id",
        "event": "submit",
        "data": {
            "id": "form_id", # Collision with event.id
            "name": "bob"
        }
    }
    e = Event(target, msg)
    # The form data 'id' should win in subscript access
    assert e["id"] == "form_id"
    # But event.id (attribute) was overwritten by the flat dict expansion in __init__
    assert e.id == "form_id" 

@pytest.mark.asyncio
async def test_event_flat_value_subscript():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "click",
        "data": "just_a_string"
    }
    e = Event(target, msg)
    assert e.value == "just_a_string"
    # Subscript should fall back to attributes even if value isn't a dict
    assert e["id"] == "123"
    assert e["missing"] is None

@pytest.mark.asyncio
async def test_event_empty_data():
    target = MagicMock()
    msg = {
        "id": "123",
        "event": "click"
        # data is missing
    }
    e = Event(target, msg)
    assert e.value is None
    assert e["id"] == "123"
