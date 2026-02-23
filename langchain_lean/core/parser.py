import re
from typing import Any

from pydantic import BaseModel, Field


class LeanGoal(BaseModel):
    """Representa una meta activa extraída del output de Lean."""

    context: list[str] = Field(default_factory=list)
    goal: str


class ParsedLeanOutput(BaseModel):
    """Salida normalizada para que el agente consuma Lean como JSON."""

    success: bool
    proof_complete: bool
    has_sorry: bool = False
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    goals: list[LeanGoal] = Field(default_factory=list)
    raw_output: str = ""


_ERROR_RE = re.compile(r"\berror:\s*(.+)", flags=re.IGNORECASE)
_WARNING_RE = re.compile(r"\bwarning:\s*(.+)", flags=re.IGNORECASE)


def parse_lean_output(raw_output: str, exit_code: int) -> ParsedLeanOutput:
    """Parsea la salida textual de Lean en una estructura estable para LLMs."""
    text = raw_output or ""
    lines = text.splitlines()

    errors = [match.group(1).strip() for line in lines if (match := _ERROR_RE.search(line))]
    warnings = [match.group(1).strip() for line in lines if (match := _WARNING_RE.search(line))]
    goals = _extract_goals(lines)

    has_sorry = "sorry" in text.lower()
    if exit_code != 0 and not errors:
        fallback = text.strip()
        if fallback:
            errors = [fallback]
    success = exit_code == 0 and not errors
    proof_complete = success and not goals and not has_sorry

    return ParsedLeanOutput(
        success=success,
        proof_complete=proof_complete,
        has_sorry=has_sorry,
        errors=errors,
        warnings=warnings,
        goals=goals,
        raw_output=text,
    )


def _extract_goals(lines: list[str]) -> list[LeanGoal]:
    goals: list[LeanGoal] = []
    for idx, line in enumerate(lines):
        marker = line.find("⊢")
        if marker < 0:
            continue

        goal_text = line[marker + 1 :].strip() or "(meta vacía)"
        context: list[str] = []

        j = idx - 1
        while j >= 0:
            candidate = lines[j].strip()
            if not candidate:
                if context:
                    break
                j -= 1
                continue
            if "error:" in candidate.lower() or "warning:" in candidate.lower():
                break
            if candidate.startswith("info:"):
                break
            context.append(candidate)
            j -= 1

        context.reverse()
        goals.append(LeanGoal(context=context, goal=goal_text))

    return goals


def parsed_output_to_dict(parsed: ParsedLeanOutput) -> dict[str, Any]:
    """Utilidad para serialización consistente en herramientas."""
    return parsed.model_dump()
