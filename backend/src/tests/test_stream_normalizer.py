import json
import os
import sys

# Ensure 'src' import path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.routes.stream import _normalize_payload  # type: ignore


def test_normalize_flattens_legacy_and_injects_cid():
    cid = "abc-123"
    legacy = json.dumps({
        "type": "content",
        "timestamp": 123.45,
        "data": {"token": "hi"}
    })

    out = _normalize_payload(cid, legacy)
    obj = json.loads(out)
    assert obj["type"] == "content"
    assert obj["token"] == "hi"
    assert obj["conversation_id"] == cid
    assert obj["ts"] == 123.45


def test_normalize_passes_through_minimal_and_adds_cid():
    cid = "xyz"
    minimal = json.dumps({"type": "progress", "progress": 0.5})
    out = _normalize_payload(cid, minimal)
    obj = json.loads(out)
    assert obj["type"] == "progress"
    assert obj["progress"] == 0.5
    assert obj["conversation_id"] == cid

