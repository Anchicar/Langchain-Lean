# langchain-lean

`langchain-lean` es una librería para usar Lean 4 desde agentes de LangChain con una experiencia similar a un REPL: ejecutar pruebas, inspeccionar metas pendientes (`tactic state`) y buscar teoremas/definiciones en Mathlib.

Actualmente el proyecto está en fase **MVP** y ya incluye:
- gestión automática de entorno con Docker,
- parser de salida de Lean a JSON entendible por LLM,
- toolkit de herramientas para agentes.

## Objetivo

Reducir la fricción para que un agente pueda trabajar con Lean sin que el usuario tenga que montar manualmente todo el entorno formal.

## Características

- `LeanRunTool`: ejecuta código Lean y devuelve resultado estructurado.
- `LeanStateTool`: devuelve metas pendientes y contexto de prueba.
- `LeanSearchTool`: busca en Loogle (`loogle.lean-lang.org`).
- `LeanREPLTool`: interfaz textual amigable (éxito/error/metas).
- `LeanToolkit`: factory para crear el set de tools de LangChain.
- Entorno Docker con fallback de imagen y workspace persistente.

## Requisitos

- Python 3.10+
- Docker Desktop (encendido y funcionando)
- Sistema con recursos suficientes para Lean/Mathlib (recomendado: 8GB+ RAM)

## Instalación

### Opción 1: desarrollo local (recomendada para este repo)

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

### Opción 2: usando Poetry

```powershell
poetry install
poetry shell
```

## Ejecución rápida (smoke test)

El script `examples/mvp_smoke_test.py` prueba las 4 tools en secuencia.

```powershell
python examples\mvp_smoke_test.py
```

Sin búsqueda web (útil si no hay red):

```powershell
python examples\mvp_smoke_test.py --skip-search
```

## Uso básico en código

### 1) Usar tools individuales

```python
from langchain_lean.tools import LeanRunTool, LeanStateTool, LeanSearchTool

run_tool = LeanRunTool()
state_tool = LeanStateTool()
search_tool = LeanSearchTool()

ok = run_tool.invoke({"code": "theorem t (n : Nat) : n + 0 = n := by simp"})
state = state_tool.invoke({"code": "theorem t (n : Nat) : n + 0 = n := by\n  induction n with\n  | zero => simp\n  | succ n ih =>"})
hits = search_tool.invoke({"query": "Nat.add_assoc", "limit": 5})
```

### 2) Usar `LeanToolkit`

```python
from langchain_lean import LeanToolkit

tools = LeanToolkit(
    include_run=True,
    include_state=True,
    include_search=True,
    include_repl=False,
).get_tools()
```

También existe helper funcional:

```python
from langchain_lean import create_lean_tools

tools = create_lean_tools(include_repl=True)
```

## Cómo se ejecuta el código Lean internamente

1. `LeanRunTool`/`LeanStateTool` inicializan `LeanEnvironmentManager`.
2. El manager valida Docker, workspace e imagen de Lean.
3. `LeanEvaluator` escribe el código en `lean_workspace/check.lean`.
4. Se ejecuta en contenedor con:
   - `lake env lean check.lean` (si `lake` existe),
   - fallback a `lean check.lean`.
5. `parse_lean_output(...)` transforma la salida en JSON (`success`, `errors`, `goals`, etc.).

## Formato de salida (resumen)

Las tools principales devuelven JSON serializado con campos como:

- `success`: compiló y verificó sin errores.
- `proof_complete`: no quedan metas y no se detectó `sorry`.
- `goals`: metas abiertas con `context` + `goal`.
- `errors`: errores de Lean o del shell.
- `warnings`: advertencias detectadas.
- `raw_output`: salida original para debug.

## Tests

Se incluye una suite mínima en `tests/`:
- parser de salida (éxito, incompleto, error),
- búsqueda mockeada de Loogle,
- construcción del toolkit.

Instalar `pytest` y correr:

```powershell
python -m pip install pytest
python -m pytest -q tests
```

## Estructura del proyecto y para qué sirve cada archivo

### Raíz

- `pyproject.toml`: metadatos del paquete, dependencias y build system.
- `README.md`: documentación principal del proyecto.
- `lean_workspace/`: workspace Lean local persistente.
- `Docker/`: Dockerfile y scripts de soporte del entorno Lean.
- `examples/`: scripts de demo/smoke test.
- `tests/`: pruebas automáticas mínimas.

### `langchain_lean/`

- `langchain_lean/__init__.py`: API pública (exports del paquete).
- `langchain_lean/toolkit.py`: `LeanToolkit` y `create_lean_tools`.

### `langchain_lean/core/`

- `langchain_lean/core/environment.py`: manejo de Docker, imagen, workspace y ejecución de comandos.
- `langchain_lean/core/evaluator.py`: ejecuta código Lean y construye `LeanExecutionResult`.
- `langchain_lean/core/parser.py`: parsea salida cruda de Lean a estructura JSON.
- `langchain_lean/core/enviroment.py`: shim de compatibilidad por typo histórico (`enviroment` -> `environment`).
- `langchain_lean/core/__init__.py`: exports del submódulo `core`.

### `langchain_lean/tools/`

- `langchain_lean/tools/run_tool.py`: `LeanRunTool`.
- `langchain_lean/tools/state_tool.py`: `LeanStateTool`.
- `langchain_lean/tools/search_tool.py`: `LeanSearchTool` (Loogle API).
- `langchain_lean/tools/repl_tool.py`: `LeanREPLTool` (respuesta textual amigable).
- `langchain_lean/tools/__init__.py`: exports del submódulo `tools`.

### `examples/`

- `examples/mvp_smoke_test.py`: validación de MVP (`run`, `state`, `search`, `repl`).
- `examples/math_agent_test.py`: ejemplo de agente LangChain con tool Lean.
- `examples/test_setup.py`: prueba manual inicial de entorno/herramienta.

### `tests/`

- `tests/conftest.py`: prepara `sys.path` para ejecutar tests sin instalar editable.
- `tests/test_parser.py`: pruebas unitarias del parser.
- `tests/test_search_tool.py`: prueba de búsqueda con `urlopen` mockeado.
- `tests/test_toolkit.py`: validación de factory/toolkit.

## Limitaciones actuales (MVP)

- No hay ejecución táctica paso a paso con estado interactivo completo.
- Dependencia fuerte de Docker local.
- Compatibilidad de versiones Lean/Mathlib aún no parametrizada al 100%.
- Integración profunda con LeanDojo aún pendiente (hay dependencia declarada, pero no backend completo en uso).

## Roadmap sugerido

- Integración opcional de backend LeanDojo para interacción táctica avanzada.
- Mejoras de caching por versión de Lean/Mathlib.
- CI/CD con tests automáticos y publicación PyPI.
- Ejemplos de agentes iterativos que cierren metas usando `LeanStateTool`.

## Licencia

MIT
