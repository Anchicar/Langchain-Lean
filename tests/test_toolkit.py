from langchain_lean.toolkit import LeanToolkit


class _DummyTool:
    pass


def test_toolkit_returns_expected_tools(monkeypatch):
    monkeypatch.setattr("langchain_lean.toolkit.LeanRunTool", _DummyTool)
    monkeypatch.setattr("langchain_lean.toolkit.LeanStateTool", _DummyTool)
    monkeypatch.setattr("langchain_lean.toolkit.LeanSearchTool", _DummyTool)
    monkeypatch.setattr("langchain_lean.toolkit.LeanREPLTool", _DummyTool)

    toolkit = LeanToolkit(include_run=True, include_state=True, include_search=True, include_repl=False)
    tools = toolkit.get_tools()

    assert len(tools) == 3
    assert all(isinstance(tool, _DummyTool) for tool in tools)
