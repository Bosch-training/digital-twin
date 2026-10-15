# Digital Twin – Assembly-Line Simulation

## Description
A demo project that models a manufacturing assembly line as a digital twin. A discrete-event simulation (SimPy) mimics stations, buffers, conveyors, and work items; a FastAPI service exposes simulation control and live state; a React dashboard visualizes throughput, cycle time, utilization, queues, and bottlenecks.

This is a demo: favor clarity and small, readable modules over production-grade infrastructure. The repo is at an early stage — the layout below is the **target structure**; create files there rather than inventing new top-level folders.

## Folder Structure
```
digital-twin/
├── .github/copilot-instructions.md   # This file
├── src/digital_twin/
│   ├── simulation/                   # SimPy engine, stations, buffers, work items
│   ├── twin/                         # Twin state model, sync of "physical" signals
│   ├── analytics/                    # KPI calculation (throughput, OEE, bottlenecks)
│   ├── api/                          # FastAPI app, routers, schemas, WebSocket stream
│   └── config/                       # Line configs (YAML) and pydantic settings
├── frontend/                         # React + TypeScript dashboard (Vite)
│   ├── src/
│   │   ├── api/                      # Typed API/WebSocket client
│   │   ├── components/               # Line view, station cards, KPI charts
│   │   ├── hooks/                    # Data-fetching and live-state hooks
│   │   └── types/                    # Types mirroring API schemas
│   └── package.json
├── data/                             # Sample/synthetic line configs and event data
├── tests/                            # Mirrors src/digital_twin/ layout
├── pyproject.toml
├── .env.example
└── README.md
```

## Modules
- **simulation**: Pure SimPy logic. No I/O, No FastAPI imports. Must be deterministic when given a random seed.
- **twin**: Holds the current state of each station/buffer and applies updates (simulated or injected sensor events).
- **analytics**: Pure functions turning simulation events/state into KPIs. No side effects.
- **api**: Thin FastAPI layer (start/stop/reset simulation, get state, get KPIs, inject faults) plus a WebSocket endpoint that streams live twin state. Business logic stays in other modules.
- **frontend**: React + TypeScript dashboard that talks to the backend only through the API/WebSocket; it contains no simulation or KPI logic beyond presentation.
- **config**: Pydantic models for line definitions (stations, process times, failure rates) loaded from YAML.

Dependency direction: `frontend → api → twin/analytics → simulation → config`. Do not introduce reverse imports, and keep `frontend/src/types` in sync with the API schemas.

## Story Workflow (mandatory)
Requests like "implement DT-xxx" must never be coded directly. Run these agents in order via subagents, skipping a step only if its output already exists and is complete:
1. `requirement-analysis` → `docs/<story-id>-analysis.md`
2. `test-spec-creator` → `docs/test-spec/<STORY-ID>-test-spec.csv` (required even when a story has no unit-level rows)
3. `unit-test-creator` → `tests/unit/` (skipped only if the CSV has no `Unit` rows with `Ready`/`Assumption`)
4. `tdd-implementation` → production code

## Technology Stack
- Python 3.11+
- SimPy (discrete-event simulation)
- FastAPI + Uvicorn, Pydantic v2 / pydantic-settings
- NumPy / Pandas (data handling)
- SQLite for persisting run results (demo scope; no external DB)
- `pyproject.toml` for dependencies; use a virtualenv (`.venv`)
- Frontend: React 18 + TypeScript (strict) built with Vite, Plotly.js (`react-plotly.js`) for charts, TanStack Query for REST data, native WebSocket for live state; Node 20+ with npm

## Testing Framework
- pytest, with `pytest-asyncio` for async API tests and `httpx` / FastAPI `TestClient` for endpoints.
- Tests live in `tests/`, mirroring `src/digital_twin/`; name files `test_<module>.py`.
- Always seed random number generators in simulation tests so results are reproducible.
- Prefer testing KPIs and station behavior (e.g., a bottleneck station limits throughput) over implementation details.
- Run: `pytest` (with coverage: `pytest --cov=digital_twin`).
- Frontend: Vitest + React Testing Library in `frontend/`, tests colocated as `*.test.tsx`; mock the API/WebSocket client, never the real backend. Run: `npm test`.

### Example unit test
`tests/analytics/test_kpis.py` — tests a pure analytics function (arrange / act / assert, no I/O):

```python
import pytest

from digital_twin.analytics.kpis import throughput_per_hour


def test_throughput_per_hour_counts_completed_items():
    # 30 items completed in 15 minutes -> 120 items/hour
    assert throughput_per_hour(completed_items=30, elapsed_s=900) == pytest.approx(120.0)


def test_throughput_per_hour_rejects_non_positive_elapsed_time():
    with pytest.raises(ValueError):
        throughput_per_hour(completed_items=10, elapsed_s=0)
```

The function under test (`src/digital_twin/analytics/kpis.py`):

```python
def throughput_per_hour(completed_items: int, elapsed_s: float) -> float:
    """Return completed work items per hour for the given elapsed simulation time."""
    if elapsed_s <= 0:
        raise ValueError("elapsed_s must be greater than 0")
    return completed_items / elapsed_s * 3600
```

## Project Specific Sources
- Line configurations: `data/*.yaml` (stations, process-time distributions, buffer sizes, failure/repair rates).
- Sample/synthetic event data: `data/` (CSV/JSON). All data is synthetic; do not add real plant data.
- Domain terms to use consistently: station, buffer, work item, cycle time, takt time, throughput, utilization, WIP, OEE, bottleneck, starvation, blocking.
- Time unit in the simulation is **seconds** unless a variable name states otherwise (e.g., `cycle_time_s`).

## Linting Rules
- Ruff for linting (`ruff check .`) with rules: `E`, `F`, `I`, `B`, `UP`, `SIM`.
- mypy for type checking (`mypy src`); all public functions require type hints.
- Max line length: 100.
- No bare `except:`; no `print` in library code (use `logging`).
- Frontend: ESLint (`npm run lint`) with `typescript-eslint`, `react-hooks`, and `jsx-a11y`; `tsc --noEmit` must pass; no `any` without a justifying comment.

## Code Formatting
- Ruff formatter (`ruff format .`), Black-compatible style, line length 100.
- Google-style docstrings for public classes/functions; skip docstrings for trivial helpers.
- Naming: `PascalCase` classes, `snake_case` functions/variables, `UPPER_SNAKE_CASE` constants; include units in names for quantities (`*_s`, `*_per_hour`).
- Use `dataclasses`/Pydantic models over loose dicts for structured data.
- Frontend: Prettier (`npm run format`); function components with hooks only; `PascalCase` component files, `camelCase` functions/variables; 2-space indent, single quotes, semicolons.

## Deployment Instructions
Demo/local deployment only:
1. `python -m venv .venv && source .venv/bin/activate`
2. `pip install -e ".[dev]"`
3. `cp .env.example .env` and adjust values.
4. API: `uvicorn digital_twin.api.main:app --reload --port 8000` (docs at `/docs`).
5. Frontend: `cd frontend && npm install && npm run dev` (Vite on port 5173; set `VITE_API_BASE_URL` to the API, e.g. `http://localhost:8000`).
6. Production build: `npm run build` produces static files in `frontend/dist`.
7. Optional: a `Dockerfile`/`docker-compose.yml` running the API and a static frontend (nginx) as two services.

## Sensitive Code Handling
- Never read, print, or commit `.env`, `.env.*` (dev/test/prod) or any secrets file; only `.env.example` may be read or edited, and it must contain placeholders only.
- Load configuration via pydantic-settings; never hard-code keys, tokens, or connection strings.
- Do not log secrets or full request bodies.
- Keep all sample data synthetic; never add real production or customer data.
- Restrict CORS origins (allow only the frontend origin) and validate all API inputs with Pydantic schemas, even in the demo.
- Frontend: only `VITE_`-prefixed variables are exposed to the browser bundle, so never put secrets in them; avoid `dangerouslySetInnerHTML`.
