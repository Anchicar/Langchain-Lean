import json

from langchain_lean.tools.search_tool import LeanSearchTool


class _FakeResponse:
    def __init__(self, payload: str):
        self._payload = payload.encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_search_tool_with_mocked_loogle(monkeypatch):
    payload = json.dumps(
        {
            "hits": [
                {"name": "Nat.add_assoc", "type": "(n m k : Nat) : _", "doc": "assoc"},
                {"name": "Nat.add_comm", "type": "(n m : Nat) : _", "doc": "comm"},
            ]
        }
    )

    def _fake_urlopen(url, timeout=12):
        assert "loogle.lean-lang.org/json" in url
        return _FakeResponse(payload)

    monkeypatch.setattr("langchain_lean.tools.search_tool.urlopen", _fake_urlopen)

    tool = LeanSearchTool()
    raw = tool.invoke({"query": "Nat.add_assoc", "limit": 1})
    result = json.loads(raw)

    assert result["query"] == "Nat.add_assoc"
    assert result["count"] == 1
    assert result["results"][0]["name"] == "Nat.add_assoc"
