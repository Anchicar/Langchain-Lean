from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

# Permite ejecutar este script desde el repo sin instalar el paquete.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from langchain_lean.tools import LeanREPLTool, LeanRunTool, LeanSearchTool, LeanStateTool


def _print_json_block(title: str, raw: str) -> None:
    print(f"\n=== {title} ===")
    try:
        parsed = json.loads(raw)
        print(json.dumps(parsed, indent=2, ensure_ascii=True))
    except json.JSONDecodeError:
        print(raw)


def _run_tool_demo() -> None:
    print("\n[1/4] LeanRunTool")
    tool = LeanRunTool()
    code = """
theorem add_zero_demo (n : Nat) : n + 0 = n := by
  simp
""".strip()
    result = tool.invoke({"code": code})
    _print_json_block("LeanRunTool result", result)


def _state_tool_demo() -> None:
    print("\n[2/4] LeanStateTool")
    tool = LeanStateTool()
    code = """
theorem add_zero_partial (n : Nat) : n + 0 = n := by
  induction n with
  | zero => simp
  | succ n ih =>
""".strip()
    result = tool.invoke({"code": code})
    _print_json_block("LeanStateTool result", result)


def _search_tool_demo(query: str) -> None:
    print("\n[3/4] LeanSearchTool")
    tool = LeanSearchTool()
    result = tool.invoke({"query": query, "limit": 5})
    _print_json_block("LeanSearchTool result", result)


def _repl_tool_demo() -> None:
    print("\n[4/4] LeanREPLTool")
    tool = LeanREPLTool()
    code = """
theorem mul_one_demo (n : Nat) : n * 1 = n := by
  simp
""".strip()
    result = tool.invoke({"code": code})
    print("\n=== LeanREPLTool result ===")
    print(result)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test del MVP de langchain-lean (run/state/search/repl)."
    )
    parser.add_argument(
        "--query",
        default="Nat.add_assoc",
        help="Consulta para LeanSearchTool (default: Nat.add_assoc).",
    )
    parser.add_argument(
        "--skip-search",
        action="store_true",
        help="Omite LeanSearchTool (útil si estás sin red).",
    )
    args = parser.parse_args(argv)

    print("Iniciando smoke test MVP de langchain-lean...")

    try:
        _run_tool_demo()
        _state_tool_demo()
        if not args.skip_search:
            _search_tool_demo(args.query)
        else:
            print("\n[3/4] LeanSearchTool omitido por --skip-search")
        _repl_tool_demo()
    except Exception as exc:  # pragma: no cover - smoke script
        print(f"\nERROR en smoke test: {exc}")
        return 1

    print("\nSmoke test finalizado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
