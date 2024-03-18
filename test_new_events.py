from htag import Tag
from htag.tag import NotBindedCaller,Caller

class T(Tag.div):
    pass

def cb(o):
    print('k')


def test_old_way_is_ok(): # <=0.7.4
    # CURRENT
    #========================================
    t=T()
    t["onclick"] = t.bind(cb) + "var x=42"
    assert isinstance(t["onclick"],Caller)
    assert t["onclick"]._befores == []
    assert t["onclick"]._afters == ["var x=42"]
    assert len(t["onclick"]._others ) == 0

    # ensure the base is ok
    t=T()
    t["onclick"] = "var x=42"
    assert isinstance(t["onclick"],str)

    t=T()
    t["onclick"] = t.bind(cb).bind(cb) + "var x=40"
    assert isinstance(t["onclick"],Caller)
    assert t["onclick"]._befores == []
    assert t["onclick"]._afters == ["var x=40"]
    assert len(t["onclick"]._others ) == 1

    t=T()
    t["onclick"] = t.bind(cb) + "var x=40"
    assert isinstance(t["onclick"],Caller)
    assert t["onclick"]._befores == []
    assert t["onclick"]._afters == ["var x=40"]
    assert len(t["onclick"]._others ) == 0

    t=T()
    t["onclick"] = "var x=40" + t.bind(cb)
    assert isinstance(t["onclick"],Caller)
    assert t["onclick"]._befores == ["var x=40"]
    assert t["onclick"]._afters == []
    assert len(t["onclick"]._others ) == 0

def test_new_events(): # >0.7.4
    # all "on*" attrs are not None, by default ...
    t=T()
    assert isinstance(t["onclick"],NotBindedCaller)

    # new syntax
    t=T()
    t["onclick"]+= "var x=2"
    assert isinstance(t["onclick"],NotBindedCaller)
    assert t["onclick"]._befores == []
    assert t["onclick"]._afters == ["var x=2"]

    t=T()
    t["onclick"] = "var x=2" + t["onclick"]
    assert isinstance(t["onclick"],NotBindedCaller)
    assert t["onclick"]._befores == ["var x=2"]
    assert t["onclick"]._afters == []

    t=T()
    t["onclick"] + "var x=43"   # does nothing .. NON SENSE !
    assert isinstance(t["onclick"],NotBindedCaller)
    assert t["onclick"]._befores == []
    assert t["onclick"]._afters == []

    # new syntax (over fucked ?!) (side effect, but works)
    t=T()
    t["onclick"].bind(cb).bind(cb) + "var x=41"
    assert isinstance(t["onclick"],Caller)
    assert t["onclick"]._befores == []
    assert t["onclick"]._afters == ["var x=41"]
    assert len(t["onclick"]._others ) == 1

def test_base():
    def test(o):
        print("kkk")

    b=Tag.button("hello")
    b["onclick"] = test
    assert ' onclick="try{interact' in str(b)

    b=Tag.button("hello")
    b["onclick"] = b.bind( test )
    assert ' onclick="try{interact' in str(b)

    b=Tag.button("hello")
    b["onclick"].bind( test )
    assert ' onclick="try{interact' in str(b)

if __name__=="__main__":

    import logging
    logging.basicConfig(format='[%(levelname)-5s] %(name)s: %(message)s',level=logging.DEBUG)
