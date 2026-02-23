from __future__ import annotations

import json
from typing import Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from langchain_lean.core.evaluator import LeanEvaluator
from langchain_lean.core.environment import LeanEnvironmentManager


class LeanStateInput(BaseModel):
    code: str = Field(..., description="Demostración parcial en Lean 4 para inspeccionar metas pendientes.")


class LeanStateTool(BaseTool):
    """Obtiene el tactic state estructurado para una prueba parcial."""

    name: str = "lean_state"
    description: str = (
        "Ejecuta una prueba Lean parcial y retorna JSON con goals abiertas, proof_complete y errores."
    )
    args_schema: Type[BaseModel] = LeanStateInput

    _env_manager: Optional[LeanEnvironmentManager] = PrivateAttr(default=None)
    _evaluator: Optional[LeanEvaluator] = PrivateAttr(default=None)

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._env_manager = LeanEnvironmentManager()
        self._env_manager.provision_environment()
        self._evaluator = LeanEvaluator(environment_manager=self._env_manager)

    def _run(self, code: str) -> str:
        if self._evaluator is None:
            self._env_manager = LeanEnvironmentManager()
            self._env_manager.provision_environment()
            self._evaluator = LeanEvaluator(environment_manager=self._env_manager)

        result = self._evaluator.evaluate_code(code)
        payload = {
            "success": result.success,
            "proof_complete": result.proof_complete,
            "has_sorry": result.has_sorry,
            "goals": result.goals,
            "errors": result.errors,
            "warnings": result.warnings,
            "raw_output": result.raw_output,
        }
        return json.dumps(payload, ensure_ascii=False)

    async def _arun(self, code: str) -> str:
        return self._run(code)
