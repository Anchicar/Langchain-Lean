from __future__ import annotations

import os
from typing import Optional

from pydantic import BaseModel, Field

from langchain_lean.core.parser import ParsedLeanOutput, parse_lean_output


class LeanExecutionResult(BaseModel):
    """Resultado normalizado de una ejecución Lean."""

    success: bool = Field(..., description="Si Lean compiló correctamente.")
    proof_complete: bool = Field(default=False, description="Si no quedan metas y no hay sorry.")
    has_sorry: bool = Field(default=False, description="Si Lean detectó uso de sorry.")
    goals: list[dict[str, object]] = Field(default_factory=list, description="Metas abiertas parseadas.")
    errors: list[str] = Field(default_factory=list, description="Errores de compilación/verificación.")
    warnings: list[str] = Field(default_factory=list, description="Warnings reportados por Lean.")
    raw_output: str = Field(default="", description="Salida cruda de Lean.")


class LeanEvaluator:
    """Ejecuta código Lean sobre Docker y retorna salida parseada."""

    def __init__(self, environment_manager: Optional["LeanEnvironmentManager"] = None):
        if environment_manager is not None:
            self.env_manager = environment_manager
        else:
            from langchain_lean.core.environment import LeanEnvironmentManager

            self.env_manager = LeanEnvironmentManager()
            self.env_manager.provision_environment()

    def evaluate_code(self, lean_code: str, filename: str = "check.lean") -> LeanExecutionResult:
        workspace_path = self.env_manager.get_workspace_abs_path()
        full_path = os.path.join(workspace_path, filename)

        try:
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(lean_code)
        except OSError as exc:
            return LeanExecutionResult(
                success=False,
                errors=[f"No se pudo escribir el archivo Lean: {exc}"],
            )

        # Preferimos `lake env lean` para respetar el workspace; si `lake` no existe,
        # hacemos fallback a `lean` para mantener el MVP usable.
        cmd = f"if command -v lake >/dev/null 2>&1; then lake env lean {filename}; else lean {filename}; fi"
        exit_code, output = self.env_manager.run_command_in_container(command=cmd, timeout=240)

        parsed: ParsedLeanOutput = parse_lean_output(output, exit_code)
        return LeanExecutionResult(
            success=parsed.success,
            proof_complete=parsed.proof_complete,
            has_sorry=parsed.has_sorry,
            goals=[goal.model_dump() for goal in parsed.goals],
            errors=parsed.errors,
            warnings=parsed.warnings,
            raw_output=parsed.raw_output,
        )
