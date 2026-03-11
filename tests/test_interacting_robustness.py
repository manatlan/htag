import asyncio
import pytest
from htag import Tag
from htag.runner import AppRunner

class MyTag(Tag.div):
    def init(self):
        self.count = 0
    def click(self):
        self.count += 1
        return self.count

@pytest.mark.asyncio
async def test_handle_event_invalid_tag_responds():
    app = AppRunner(MyTag)
    
    # Simulate an event to a non-existent tag ID
    msg = {
        "id": "non-existent-id",
        "event": "click",
        "data": {"callback_id": "cb123"}
    }
    
    responses = []
    class MockWS:
        async def send_text(self, text):
            responses.append(text)
        async def accept(self): pass
        async def receive_text(self): pass
        
    await app.handle_event(msg, MockWS())
    
    assert len(responses) == 1
    import json
    from htag.utils import _obf_loads
    resp = _obf_loads(responses[0], None)
    assert resp["action"] == "update"
    assert resp["callback_id"] == "cb123"
    assert resp["result"] is None

@pytest.mark.asyncio
async def test_handle_event_missing_event_responds():
    app = AppRunner(MyTag)
    
    # Tag exists but event doesn't
    tag = MyTag()
    app.add(tag) 
    
    msg = {
        "id": tag.id,
        "event": "unknown_event",
        "data": {"callback_id": "cb456"}
    }
    
    responses = []
    class MockWS:
        async def send_text(self, text):
            responses.append(text)
            
    await app.handle_event(msg, MockWS())
    
    assert len(responses) == 1
    from htag.utils import _obf_loads
    resp = _obf_loads(responses[0], None)
    assert resp["callback_id"] == "cb456"
