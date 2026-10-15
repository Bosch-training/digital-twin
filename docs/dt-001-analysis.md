# Requirement Analysis: DT-001 (Project skeleton and health endpoint)

**Sources:** `docs/digital_twin_assembly_line_testing_requirements.md`, `docs/DT-001.md`, cross-references in DT-007, DT-008, DT-009, DT-012, DT-013, DT-014.
**In scope:** FR-01, NFR-04 (health part), NFR-05 (local-run/config part), TR-01 (Unit/API/Smoke levels relevant to `/health`), TC-01.
**Out of scope for DT-001:** `/simulate`, validation (FR-02 to FR-07), Docker, CI, AWS deployment (per DT-001 "Out of scope").

## 1. Requirement summary

| ID | Atomic testable statement | Priority | Source |
|---|---|---|---|
| FR-01.a | The service exposes `GET /health`. | High | FR-01 |
| FR-01.b | `GET /health` returns HTTP 200. | High | FR-01, DT-001 AC1 |
| FR-01.c | Response body is JSON with `status` equal to `"healthy"` (DT-001 narrows body to exactly `{"status": "healthy"}`). | High | FR-01, DT-001 AC1 |
| FR-01.d | `GET /health` does not start a simulation or modify simulation state. | High | FR-01, DT-001 Scope, AC2 |
| FR-01.e | Repeated `GET /health` calls return identical responses. | Medium | DT-001 AC2 |
| NFR-04.a | `/health` is usable as a deployment smoke-test endpoint (stable, side-effect free, 200 when service is up). | Medium | NFR-04, DT-001 |
| NFR-05.a | App starts locally with `uvicorn app.main:app`. | High | DT-001 Scope, NFR-05 |
| NFR-05.b | Configuration is read from environment variables only; no hard-coded AWS account IDs, credentials, or environment-specific values. | Medium | NFR-05, DT-001 Scope |
| SK-01 | Package layout exists: `app/` (`main.py`, `__init__.py`), `tests/unit/`, `tests/api/`, `requirements.txt`, `.gitignore`. | Medium | DT-001 Scope |
| SK-02 | `requirements.txt` has pinned versions. | Medium | DT-001 AC4 |
| SK-03 | `pytest` run from repo root discovers tests under `tests/`. | High | DT-001 AC3 |
| DoD-01 | TC-01 passes locally, lint passes, no secrets committed. | High | DT-001 DoD |
| TR-01.a | API-level test uses `TestClient` against `/health` only, independent of other stories. | Medium | DT-001 Independent test approach, TR-01 |

## 2. Test conditions

| Cond. ID | Req. ID | Type | Input | Expected result |
|---|---|---|---|---|
| TCOND-01 | FR-01.a/b/c | Positive / smoke | `GET /health`, no body | HTTP 200; JSON body `{"status": "healthy"}`; `Content-Type: application/json` (ASSUMPTION: header check) |
| TCOND-02 | FR-01.c | Positive | `GET /health` | Body has `status` key; value is exactly the string `healthy` (case-sensitive) |
| TCOND-03 | FR-01.e, NFR-04.a | Determinism | `GET /health` called N times (e.g. 3) in one process | Every response has identical status code and body |
| TCOND-04 | FR-01.d | State isolation | Call `GET /health`, then (once DT-005 exists) `POST /simulate` valid request | Simulate result is the same as without a preceding health call; no simulation state created by `/health` |
| TCOND-05 | FR-01.d | Regression | Mock/spy simulator in `app`; call `GET /health` | Simulator is never invoked |
| TCOND-06 | FR-01.a | Negative | `POST /health` | HTTP 405 (ASSUMPTION: framework default; not specified in docs) |
| TCOND-07 | FR-01.a | Negative | `GET /healthz`, `GET /health/` | Behavior documented, not asserted unless clarified (see A-03) |
| TCOND-08 | FR-01.b | Boundary / robustness | `GET /health?foo=bar` | Still HTTP 200 with the same body (ASSUMPTION) |
| TCOND-09 | NFR-05.a | Smoke | Start `uvicorn app.main:app` locally; `GET /health` over HTTP | HTTP 200, healthy body |
| TCOND-10 | NFR-05.b | Negative / static | Start app with no AWS-related env vars set; scan `app/` for AWS account IDs, keys, hard-coded hosts | App starts and `/health` returns 200; no hard-coded values found |
| TCOND-11 | NFR-05.b | Positive | Start app with an optional env var (e.g. port) set | App honors it (ASSUMPTION: only if such a variable is implemented; DT-012 mentions a port variable, not DT-001) |
| TCOND-12 | SK-01 | Static | Inspect repo | `app/__init__.py`, `app/main.py`, `tests/unit/`, `tests/api/`, `requirements.txt`, `.gitignore` exist |
| TCOND-13 | SK-02 | Static | Parse `requirements.txt` | Every dependency is pinned (e.g. `==`), none unpinned or open-ranged |
| TCOND-14 | SK-03 | Smoke | Run `pytest` from repo root | Exit 0; TC-01 test is collected from `tests/api/` |
| TCOND-15 | DoD-01 | Static | Run linter and secret check (e.g. `git grep` for keys; confirm `.env*` ignored in `.gitignore`) | Lint passes; no secrets committed |
| TCOND-16 | NFR-04.a | Error / reliability | (Future, DT-007) Send an invalid `/simulate` request, then `GET /health` | HTTP 200 (covered by NFR-03 / DT-007, not DT-001) |

## 3. Ambiguities and conflicts

| # | Finding | Source | Risk | Clarifying question |
|---|---|---|---|---|
| A-01 | FR-01 says "JSON containing `status: "healthy"`" (allows extra fields), while DT-001 specifies the body as exactly `{"status": "healthy"}`. | FR-01 vs DT-001 AC1 | Medium: tests may over- or under-assert. | Is the body exact-match, or may extra fields (version, timestamp) be added later? ASSUMPTION: exact match for DT-001. |
| A-02 | "Identical response and no state changes" (AC2) is hard to verify without defined state. At DT-001 there is no simulation code. | DT-001 AC2 | Low: untestable at this story. | What observable state should be checked? ASSUMPTION: only response equality now; state check deferred to DT-005. |
| A-03 | Behavior for other methods (`POST /health`), trailing slash, and query strings is not specified. | FR-01 | Low | Should non-GET methods return 405, and is `/health/` expected to work or redirect? |
| A-04 | NFR-05 is cited in DT-001, but its Docker clause is out of scope (Docker is deferred to DT-012). Only the config/no-hard-coding clause applies. | NFR-05 vs DT-001 Out of scope; DT-012 | Low: scope creep or false "no coverage". | Confirm DT-001 covers only the "no hard-coded values / env-var config" part of NFR-05. |
| A-05 | "Configuration comes from environment variables only" but no variable is named or required in DT-001. | DT-001 Scope, NFR-05 | Low: untestable beyond static scan. | Does DT-001 need any env var (e.g. port, log level)? If none, is the condition only a static scan? |
| A-06 | NFR-04 "health endpoint suitable for a smoke test" has no measurable criterion (e.g. response time, no dependencies). | NFR-04 | Low | Is a response-time threshold expected? (NFR-06 only applies to valid `/simulate`.) |
| A-07 | "Lint passes" has no named tool in the requirements docs. `.github/copilot-instructions.md` names Ruff (`ruff check .`) and mypy. | DT-001 DoD | Low | Confirm Ruff is the lint tool for the `app/` layout. |
| A-08 | CONFLICT: `.github/copilot-instructions.md` targets `src/digital_twin/`, `pyproject.toml`, SimPy, a React dashboard and a WebSocket stream. DT-001 specifies `app/`, `requirements.txt` and a plain FastAPI API. | copilot-instructions vs DT-001 | Medium: wrong layout/paths in tests. | Treated `docs/` as authoritative for this analysis (`app/`, `requirements.txt`). Confirm that the instructions file will be aligned. |
| A-09 | TC-01 covers only HTTP 200 and healthy status. Determinism (AC2) and no-side-effects (FR-01) have no TC-xx. | TR-02 TC-01 vs FR-01, DT-001 AC2 | Medium: gap in coverage. | Should extra cases (repeat call, no state change) be added as TC-01 sub-cases or as new IDs? |
| A-10 | The Python version is not stated in the requirements docs. | DT-001 | Low | Which Python version should `requirements.txt` pins target? (copilot-instructions says 3.11+.) |

## 4. Traceability matrix

| Requirement | Test case (TR-02) | Story | Coverage / gap |
|---|---|---|---|
| FR-01 (200 + healthy) | TC-01 | DT-001 | Covered |
| FR-01 (no side effects) | None | DT-001 (AC2); DT-005 (regression use) | GAP: no TC-xx; covered by TCOND-03/04/05 |
| NFR-04 (health for smoke test) | TC-01 (indirect) | DT-001; DT-014 (deployed smoke); DT-008 (logging) | Partial: smoke use in DT-014; no TC-xx for the smoke-test role |
| NFR-05 (no hard-coded config) | None | DT-001; DT-012 (Docker); DT-013 (AWS) | GAP: no TC-xx; covered by static scan TCOND-10 |
| NFR-05 (runs in Docker) | None | DT-012 | Out of scope for DT-001 |
| TR-01 Unit | N/A for DT-001 (no logic) | DT-002 onward | Not applicable |
| TR-01 API | TC-01 | DT-001 | Covered |
| TR-01 Smoke | TC-01 (local), DT-014 (deployed) | DT-001, DT-014 | Local covered; deployed out of scope |
| TR-01 Regression | TC-01 re-run in full suite | DT-001, DT-010, DT-011 | Covered by suite re-run |
| TR-01 Performance sanity | None | n/a | Not applicable to `/health` (NFR-06 targets `/simulate`) |
| TR-02 TC-02 to TC-22 | n/a | DT-002 to DT-007 | Out of scope for DT-001 |
| Skeleton, pinning, pytest discovery | None | DT-001 | GAP: no TC-xx; covered by TCOND-12/13/14 |

## 5. Proposed acceptance criteria

Source ACs exist for FR-01 and the skeleton. Added criteria for gaps:

- **NFR-05 / Scope:** **Given** no AWS-related environment variables are set, **when** the app is started with `uvicorn app.main:app`, **then** it starts and `GET /health` returns 200 with `{"status": "healthy"}`.
- **NFR-05:** **Given** the repository source, **when** scanned for AWS account IDs, credentials, or environment-specific URLs, **then** none are found.
- **FR-01 (no side effects):** **Given** the simulator is replaced by a spy, **when** `GET /health` is called, **then** the simulator is never invoked.
- **FR-01 (methods, ASSUMPTION):** **Given** the app is running, **when** `POST /health` is called, **then** the response is HTTP 405 (pending A-03).
- **Skeleton:** **Given** a clean checkout, **when** `pytest` is run from the repo root, **then** it exits 0 and discovers the TC-01 test under `tests/api/`.
- **SK-02:** **Given** `requirements.txt`, **when** inspected, **then** every entry has a pinned version.

## 6. Validation checklist

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Every FR, NFR, TR in scope appears in the traceability table with a test condition or "no coverage" flag | Pass | FR-01, NFR-04, NFR-05, TR-01 covered; gaps flagged (A-09). FR-02 to FR-08, NFR-01 to NFR-03, NFR-06 are out of scope for DT-001. |
| 2 | FR-02 boundaries have min/max/below/above conditions | N/A | FR-02 is not in DT-001 scope (`/simulate` excluded); handled in DT-004. |
| 3 | FR-05 categories map to HTTP 400 and the FR-07 error structure | N/A | Validation is not in DT-001 scope; handled in DT-004, DT-006, DT-007. |
| 4 | Expected totals for PASS and FAIL are correct | N/A | No simulation in DT-001; PASS = assembly + packaging, FAIL = assembly (DT-002/003). |
| 5 | Each finding cites a source ID, each ambiguity has a question, each assumption is labeled | Pass | A-01 to A-10 cite sources and carry questions; assumptions marked ASSUMPTION. |
| 6 | No condition relies on real-time sleeps, random data, or AWS credentials (NFR-02) | Pass | TCOND-01 to TCOND-16 use none; TCOND-10 runs with AWS variables unset. |
