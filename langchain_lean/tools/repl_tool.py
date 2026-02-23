from __future__ import annotations

import json
from typing import Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from langchain_lean.tools.run_tool import LeanRunTool


class LeanREPLInput(BaseModel):
    code: str = Field(..., description="Código Lean 4 para ejecutar en modo REPL.")


class LeanREPLTool(BaseTool):
    """Interfaz amigable para agentes que esperan texto estilo REPL."""

    name: str = "lean_repl"
    description: str = (
        "REPL de Lean 4: ejecuta un bloque de código y devuelve éxito, metas pendientes o errores."
    )
    args_schema: Type[BaseModel] = LeanREPLInput

    _run_tool: Optional[LeanRunTool] = PrivateAttr(default=None)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._run_tool = LeanRunTool()

    def _run(self, code: str) -> str:
        if self._run_tool is None:
            self._run_tool = LeanRunTool()

        raw = self._run_tool.run(code)
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            return raw

        if not result.get("success", False):
            errors = "\n".join(result.get("errors") or ["Error desconocido"])
            return f"ERROR LEAN:\n{errors}"

        if result.get("proof_complete", False):
            return "EXITO: demostración completa (sin metas pendientes)."

        goals = result.get("goals") or []
        if goals:
            lines = ["DEMOSTRACION INCOMPLETA:"]
            for idx, goal in enumerate(goals, start=1):
                lines.append(f"Goal {idx}: {goal.get('goal')}")
                context = goal.get("context") or []
                for ctx_line in context:
                    lines.append(f"  {ctx_line}")
            return "\n".join(lines)

        return "Demostración compilada, pero Lean reportó estado no final."

    async def _arun(self, code: str) -> str:
        return self._run(code)
