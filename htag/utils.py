import json
from typing import Any

def _obf_dumps(obj: Any, key: str | None) -> str:
    if key:
        import base64

        bdata = json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
        bkey = key.encode("utf-8")
        res = bytearray(len(bdata))
        for i in range(len(bdata)):
            res[i] = bdata[i] ^ bkey[i % len(bkey)]
        return base64.b64encode(res).decode("ascii")
    return json.dumps(obj)


def _obf_loads(data: str, key: str | None) -> Any:
    if key:
        import base64

        bdata = base64.b64decode(data)
        bkey = key.encode("utf-8")
        res = bytearray(len(bdata))
        for i in range(len(bdata)):
            res[i] = bdata[i] ^ bkey[i % len(bkey)]
        return json.loads(res.decode("utf-8"))
    return json.loads(data)
