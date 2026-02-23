from __future__ import annotations

from dataclasses import dataclass

from langchain_lean.tools.repl_tool import LeanREPLTool
from langchain_lean.tools.run_tool import LeanRunTool
from langchain_lean.tools.search_tool import LeanSearchTool
from langchain_lean.tools.state_tool import LeanStateTool


@dataclass
class LeanToolkit:
    """Factory de herramientas Lean para agentes LangChain."""

    include_run: bool = True
    include_state: bool = True
    include_search: bool = True
    include_repl: bool = False

    def get_tools(self) -> list:
        tools = []
        if self.include_run:
            tools.append(LeanRunTool())
        if self.include_state:
            tools.append(LeanStateTool())
        if self.include_search:
            tools.append(LeanSearchTool())
        if self.include_repl:
            tools.append(LeanREPLTool())
        return tools


def create_lean_tools(
    include_run: bool = True,
    include_state: bool = True,
    include_search: bool = True,
    include_repl: bool = False,
) -> list:
    """Devuelve una lista de herramientas Lean listas para usar en un agente."""
    return LeanToolkit(
        include_run=include_run,
        include_state=include_state,
        include_search=include_search,
        include_repl=include_repl,
    ).get_tools()
