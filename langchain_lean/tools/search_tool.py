from __future__ import annotations

import json
from typing import Type
from urllib.parse import quote_plus
from urllib.request import urlopen

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class LeanSearchInput(BaseModel):
    query: str = Field(..., description="Consulta para buscar definiciones/teoremas en Lean.")
    limit: int = Field(default=5, ge=1, le=20, description="Cantidad máxima de resultados.")


class LeanSearchTool(BaseTool):
    """Busca términos Lean en Loogle."""

    name: str = "lean_search"
    description: str = (
        "Busca definiciones y teoremas de Lean/Mathlib usando Loogle y retorna resultados en JSON."
    )
    args_schema: Type[BaseModel] = LeanSearchInput

    def _run(self, query: str, limit: int = 5) -> str:
        encoded = quote_plus(query)
        api_url = f"https://loogle.lean-lang.org/json?q={encoded}"
        web_url = f"https://loogle.lean-lang.org/?q={encoded}"

        try:
            with urlopen(api_url, timeout=12) as response:
                payload = json.loads(response.read().decode("utf-8"))

            if isinstance(payload, dict):
                items = payload.get("hits") or payload.get("results") or []
            elif isinstance(payload, list):
                items = payload
            else:
                items = []

            normalized = []
            for item in items[:limit]:
                normalized.append(
                    {
                        "name": item.get("name") or item.get("declName") or item.get("title"),
                        "type": item.get("type") or item.get("signature"),
                        "doc": item.get("doc"),
                        "source": item.get("source") or web_url,
                    }
                )

            return json.dumps(
                {
                    "query": query,
                    "count": len(normalized),
                    "results": normalized,
                    "source": web_url,
                },
                ensure_ascii=False,
            )
        except Exception as exc:
            return json.dumps(
                {
                    "query": query,
                    "count": 0,
                    "results": [],
                    "source": web_url,
                    "error": f"No se pudo consultar Loogle API: {exc}",
                },
                ensure_ascii=False,
            )

    async def _arun(self, query: str, limit: int = 5) -> str:
        return self._run(query=query, limit=limit)
