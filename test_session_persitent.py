from htag.runners.commons import SessionFile
import os,pytest

def test_SessionFile():
    f="aeff.json"
    try:
        assert not os.path.isfile(f)

        s=SessionFile(f)
        s["hello"]=42
        s["hello"]+=1
        assert s["hello"]==43

        assert len(s)==1

        assert "jo" not in s

        with pytest.raises(Exception):
            s["jo"]

        with pytest.raises(Exception):
            del s["jo"]

        del s["hello"]

        assert not os.path.isfile(f)
    finally:
        if os.path.isfile(f):
            os.unlink(f)