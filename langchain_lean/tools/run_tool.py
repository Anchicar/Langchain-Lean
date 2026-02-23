from __future__ import annotations

import json
from typing import Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from langchain_lean.core.evaluator import LeanEvaluator, LeanExecutionResult
from langchain_lean.core.environment import LeanEnvironmentManager


class LeanRunInput(BaseModel):
    code: str = Field(..., description="Código Lean 4 completo a ejecutar.")


class LeanRunTool(BaseTool):
    """Ejecuta código Lean 4 y retorna JSON con resultado estructurado."""

    name: str = "lean_run"
    description: str = (
        "Ejecuta código Lean 4 en un entorno Dockerizado y retorna JSON con success, goals, errors y warnings."
    )
    args_schema: Type[BaseModel] = LeanRunInput

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

        result: LeanExecutionResult = self._evaluator.evaluate_code(code)
        return json.dumps(result.model_dump(), ensure_ascii=False)

    async def _arun(self, code: str) -> str:
        return self._run(code)
