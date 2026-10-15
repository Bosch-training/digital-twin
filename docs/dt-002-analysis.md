# Requirement Analysis: DT-002 (Simulator core - successful (PASS) flow)

**Sources:** `docs/digital_twin_assembly_line_testing_requirements.md`, `docs/DT-002.md`, cross-references in DT-003, DT-005, DT-006, DT-007, DT-009, DT-015; `.github/copilot-instructions.md` (structure/tooling only).
**In scope:** FR-03, FR-06 (logic level), NFR-01, NFR-02, TR-01 (Unit level), TC-02 (unit), TC-18 (unit), TC-21. Pure-Python simulator for the `PASS` path; no HTTP.
**Out of scope for DT-002:** `FAIL` handling (DT-003, FR-04, TC-03, TC-20), input validation (DT-004, FR-02/FR-05), HTTP behavior and error structure (DT-005, DT-006, FR-07), documentation (DT-009), and the documented out-of-scope items (PLC/sensor integration, authentication, persistence, ML, HA/autoscaling, production-grade performance SLAs).

## 1. Requirement summary

| ID | Atomic testable statement | Priority | Source |
|---|---|---|---|
| FR-03.a | For valid input with `inspection_result` `PASS`, the simulator processes the product through Assembly, then Inspection, then Packaging, in that order. | High | FR-03, DT-002 Scope |
| FR-03.b | The overall status is `COMPLETED`. | High | FR-03, DT-002 Scope |
| FR-03.c | The result includes `product_id` (the input value), `status`, `stations[]` and `total_simulated_time_seconds`. | High | FR-03, DT-002 Scope |
| FR-03.d | Assembly station result: `status` `COMPLETED`, `duration_seconds` = `assembly_time_seconds`. | High | FR-03, DT-002 Scope |
| FR-03.e | Inspection station result: `status` `PASS`, `duration_seconds` = 0. | High | FR-03, DT-002 Scope |
| FR-03.f | Packaging station result: `status` `COMPLETED`, `duration_seconds` = `packaging_time_seconds`. | High | FR-03, DT-002 Scope |
| FR-03.g | `total_simulated_time_seconds` = `assembly_time_seconds + packaging_time_seconds`. | High | FR-03, DT-002 AC1, TC-21 |
| FR-03.h | Field names and station order do not vary between calls. | High | FR-03 |
| FR-03.i | The simulator does not sleep or wait in real time; a 300 s assembly returns immediately. | High | FR-03, DT-002 AC3, NFR-02 |
| FR-06.a | Identical valid input yields an equal result (outcome, station order, statuses, total). | High | FR-06, DT-002 AC2, TC-18 |
| FR-06.b | The result does not depend on random values, wall-clock delays or external services. | High | FR-06, DT-002 Scope |
| NFR-01.a | Simulation logic is separate from API/validation: the simulator module has no import from the API layer and no FastAPI imports. | High | NFR-01, DT-002 DoD, Independent test approach |
| NFR-01.b | Type hints are present on the simulate function and the result model. | Medium | NFR-01, DT-002 DoD |
| NFR-01.c | Clear names, small functions, no duplicated simulation rules (review-only, not mechanically testable). | Low | NFR-01 |
| NFR-02.a | The simulator is testable by direct import, without starting an HTTP server. | High | NFR-02, DT-002 Independent test approach |
| NFR-02.b | Simulator and its tests need no AWS credentials or real infrastructure. | High | NFR-02 |
| NFR-02.c | Tests do not depend on real-time sleeps or random data. | High | NFR-02, DT-002 Scope |
| SC-01 | Inputs are assumed valid; the simulator performs no validation. | Medium | DT-002 Scope, Out of scope |
| TR-01.a | Unit tests are plain pytest, use parametrized time combinations and assert the exact station list, not only the total. | Medium | TR-01, DT-002 Independent test approach |
| DoD-01 | Unit tests pass; type hints present; no import from the API layer. | High | DT-002 DoD |

## 2. Test conditions

All inputs are synthetic. Notation: `(assembly_time_seconds, inspection_result, packaging_time_seconds)`; `product_id` is `PROD-001` unless stated. Target: the `simulate` function (see A-01, A-02 for module and test location).

| Cond. ID | Req. ID | Type | Input | Expected result |
|---|---|---|---|---|
| TCOND-01 | FR-03.a/b/c, TC-02 | Positive | `(30, PASS, 10)` | Overall `status` = `COMPLETED`; `product_id` = `PROD-001` |
| TCOND-02 | FR-03.a, TR-01.a | Positive | `(30, PASS, 10)` | `stations` has exactly 3 entries; `station` names in order `Assembly`, `Inspection`, `Packaging` |
| TCOND-03 | FR-03.d/e/f | Positive | `(30, PASS, 10)` | Station `status` values in order: `COMPLETED`, `PASS`, `COMPLETED` |
| TCOND-04 | FR-03.d/e/f | Positive | `(30, PASS, 10)` | `duration_seconds` in order: 30, 0, 10 |
| TCOND-05 | FR-03.g, TC-21 | Positive | `(30, PASS, 10)` | `total_simulated_time_seconds` = 40 |
| TCOND-06 | FR-03 | Positive | FR-03 example request | Result equals the FR-03 example response field for field |
| TCOND-07 | FR-03.c/h | Positive | `(30, PASS, 10)` | Result has `product_id`, `status`, `stations`, `total_simulated_time_seconds`; each station has `station`, `status`, `duration_seconds` (exact-set check only if A-08 is resolved) |
| TCOND-08 | FR-03.d/e/f/g | Positive | `(30, PASS, 10)` | `duration_seconds` values and total are integers (ASSUMPTION, see A-09) |
| TCOND-09 | FR-03.g | Boundary | `(1, PASS, 1)` | Durations 1/0/1; total 2 |
| TCOND-10 | FR-03.g | Boundary | `(300, PASS, 120)` | Durations 300/0/120; total 420 |
| TCOND-11 | FR-03.g | Boundary | `(1, PASS, 120)` and `(300, PASS, 1)` | Totals 121 and 301; durations map to the right stations |
| TCOND-12 | FR-03.d/f/g | Positive (swap guard) | `(120, PASS, 5)` and `(5, PASS, 120)` | Totals both 125; durations 120/0/5 and 5/0/120 respectively |
| TCOND-13 | FR-03.c | Boundary | `product_id` of 1 character (`A`) and of 50 characters | `product_id` in the result equals the input |
| TCOND-14 | FR-03.i, NFR-02.c | Positive | `(300, PASS, 120)` with `time.sleep` and `asyncio.sleep` patched to fail the test if called | Returns a result; no sleep call |
| TCOND-15 | FR-03.i | Smoke | `(300, PASS, 120)` | Returns well under 1 s (ASSUMPTION: threshold borrowed from NFR-06; secondary to TCOND-14, see A-14) |
| TCOND-16 | FR-06.b, NFR-02.c | Determinism (static) | Scan simulator module source/imports | No import of `time`, `random`, `datetime`, `asyncio`, `socket`, `os`, `boto3`, `requests`, `httpx` (ASSUMPTION: list is indicative, see A-14) |
| TCOND-17 | NFR-02.b | Positive | `(30, PASS, 10)` with all `AWS_*` environment variables removed | Same result as TCOND-06; no credentials needed |
| TCOND-18 | FR-06.a, TC-18 | Determinism | `(30, PASS, 10)` called twice | The two results are equal |
| TCOND-19 | FR-06.a | Determinism | `(30, PASS, 10)` called 100 times | All results equal the first |
| TCOND-20 | FR-06.a | State isolation | Call A `(30, PASS, 10)`, then B `(300, PASS, 120)`, then A again | Third result equals first; B gives its own correct result (no state leaks between calls) |
| TCOND-21 | FR-06.a | State isolation | Call A twice; modify the first result object's `stations` list (ASSUMPTION: result is mutable) | Second result is unaffected (no shared mutable state) |
| TCOND-22 | NFR-01.a, NFR-02.a | Static | Import the simulator module in a clean interpreter; scan imports | No import of `fastapi`, `starlette`, or the API package/`main`; no `TestClient` or server needed |
| TCOND-23 | NFR-01.b | Static | Inspect `simulate` signature and result model; run the type checker | Parameters, return type and model fields are annotated; type checker reports no errors in the module |
| TCOND-24 | FR-03.g (derived) | Positive | Parametrized set: TCOND-04, 09, 10, 11, 12 inputs | `total_simulated_time_seconds` = sum of the three `duration_seconds`; Inspection duration is 0 in every case |
| TCOND-25 | DoD-01, DT-003 DoD | Regression | Re-run the DT-002 tests after DT-003 (`FAIL` flow) is added | All DT-002 tests still pass unchanged |

No error-handling or negative conditions are derived: invalid input is handled in DT-004 (SC-01) and `FAIL` in DT-003.

## 3. Ambiguities and conflicts

| # | Finding | Source | Risk | Clarifying question |
|---|---|---|---|---|
| A-01 | CONFLICT: DT-002 places the simulator in `app/simulator.py`; `copilot-instructions.md` targets `src/digital_twin/simulation/`. Resolution: behavior from `docs/`, structure from instructions, so the target is `digital_twin.simulation.simulator`. | DT-002 Summary vs copilot-instructions | Medium: tests import a wrong path | Confirm the module path. The workspace currently contains `app/` and `src/digital_twin/api/` only. |
| A-02 | CONFLICT: tests for DT-002 are "unit" and the workflow writes them to `tests/unit/` (the repo already has `tests/unit/`), while instructions say `tests/` mirrors `src/digital_twin/` (e.g. `tests/simulation/test_simulator.py`). | DT-002 Independent test approach, requirements doc section 10 vs copilot-instructions | Low | Should simulator tests go to `tests/simulation/` (mirror layout) or `tests/unit/test_simulator.py`? |
| A-03 | SimPy is mandated by instructions (simulation = "pure SimPy logic") but no requirement in `docs/` mentions it; DT-002 says pure Python with no waiting. No conditions derived. | copilot-instructions vs FR-03, DT-002 | Medium | Must the simulator use SimPy, or plain arithmetic as DT-002 implies? |
| A-04 | React dashboard appears only in instructions; no requirement in `docs/`. No conditions derived. | copilot-instructions | Low | Is the dashboard part of any story? Confirm it is excluded from DT-002. |
| A-05 | WebSocket live-state stream appears only in instructions; no requirement in `docs/`. No conditions derived. | copilot-instructions | Low | Is a WebSocket stream required anywhere in DT-001 to DT-015? |
| A-06 | SQLite persistence of run results appears only in instructions; `docs/` lists database persistence as out of scope. No conditions derived. | copilot-instructions vs requirements doc 3.2 | Low | Confirm SQLite is excluded (docs say persistence is out of scope). |
| A-07 | KPIs/OEE/throughput analytics appear only in instructions; no requirement in `docs/`. No conditions derived. | copilot-instructions | Low | Are KPIs/OEE required, or is `total_simulated_time_seconds` the only metric? |
| A-08 | "Typed result object" / "result model" does not say dataclass, Pydantic model or dict, nor where it lives (the docs layout has `app/models.py` for API models). It also does not say whether the result is mutable, or whether extra fields (e.g. `reason`, proposed by DT-003 for FAIL) exist on PASS (absent vs `None`). | DT-002 Summary/Scope, DT-003 | Medium: attribute vs key access; exact-field assertions may break after DT-003 | Which type is the result model, where is it defined, and is `reason` absent or `None` on PASS? ASSUMPTION: attribute access, no `reason` on PASS. |
| A-09 | Function name is "such as `simulate(...)`"; positional vs keyword use, and the types of `inspection_result` and statuses (`str` vs `Enum`) are not defined. Duration type (`int` vs `float`) is not stated though the examples are integers. | DT-002 Scope, FR-02, FR-03 | Medium | Is the signature exactly `simulate(product_id, assembly_time_seconds, inspection_result, packaging_time_seconds)`? Are statuses plain strings (or `str` enums comparable to strings)? Are durations `int`? |
| A-10 | `product_id` echo: FR-02 validates "non-empty after trimming" but FR-03 only says "include the product ID". Unknown whether leading/trailing whitespace is preserved. | FR-02, FR-03 | Low | Does the simulator echo `product_id` unchanged? ASSUMPTION: yes (inputs are valid and already normalized by DT-004). |
| A-11 | TC-02 is defined as "HTTP 200; COMPLETED; all stations run" (API level) but DT-002 uses it as a unit test; the HTTP part is not testable here. TC-21's level is not stated. | TR-02 vs DT-002 | Low | Confirm unit-level TC-02 asserts only `COMPLETED` and all three stations. |
| A-12 | No TC-xx covers boundaries at simulator level: TC-04/05/08/09 are API-level (DT-005). TCOND-09 to TCOND-11 are added as unit-level boundary checks of the totals. | TR-02, DT-005 | Low | Accept unit-level boundary checks as additional cases (not new TC-xx), or assign new IDs? |
| A-13 | Behavior of the simulator for invalid input and for `inspection_result` `FAIL` in DT-002 is undefined ("inputs assumed valid"; FAIL is DT-003). Calling `FAIL` before DT-003 may return a wrong PASS-style result. | DT-002 Scope/Out of scope | Low | Should DT-002 raise (e.g. `NotImplementedError`) for `FAIL`, or is it unspecified until DT-003? No tests derived. |
| A-14 | "Returns immediately" has no measurable threshold; NFR-06 (1 s sanity) targets valid API requests, not cited by DT-002. The forbidden-import list for the static check is not defined in the docs. Time-based assertions risk flakiness. | DT-002 AC3, FR-03, NFR-02, NFR-06 | Low | Is a 1 s threshold acceptable for the unit-level check? Prefer the patched-sleep approach (TCOND-14) as the primary check? |
| A-15 | NFR-01 "clear names, small functions, no duplicated rules" and "no import from the API layer" mix subjective and mechanical items; only the import and type-hint parts are testable. | NFR-01, DT-002 DoD | Low | Is code review acceptable evidence for NFR-01.c? |
| A-16 | CONFLICT: DT-002 DoD says "type hints present" without a tool; instructions name Ruff (`ruff check .`) and mypy (`mypy src`), line length 100. | DT-002 DoD vs copilot-instructions | Low | Confirm mypy/Ruff are the checks used. Instructions are used for tooling. |
| A-17 | Instructions require simulation to be "deterministic when given a random seed", while `docs/` forbids randomness entirely (FR-06). No seed parameter is derived. | copilot-instructions vs FR-06 | Low | Confirm the simulator takes no seed and has no randomness. |

## 4. Traceability matrix

| Requirement | Test case (TR-02) | Story | Coverage / gap |
|---|---|---|---|
| FR-03.a/b/c/d/e/f | TC-02 (unit) | DT-002; DT-005 (API level) | Covered; TCOND-01 to TCOND-04 |
| FR-03.g | TC-21 | DT-002; DT-005 (API level) | Covered; TCOND-05, TCOND-09 to TCOND-12, TCOND-24 |
| FR-03.h (field names, order stable) | None | DT-002; DT-005, DT-009 (documentation) | GAP: no TC-xx; covered by TCOND-07 |
| FR-03.i (no sleeping) | None (TC-21 only checks the total) | DT-002; DT-007 (performance sanity) | GAP: no TC-xx; covered by TCOND-14, TCOND-15 |
| FR-06.a | TC-18 (unit) | DT-002; DT-005, DT-007 (API level) | Covered; TCOND-18 to TCOND-21 |
| FR-06.b | None | DT-002 | GAP: no TC-xx; covered by TCOND-16 |
| NFR-01.a/b | None | DT-002 DoD | GAP: no TC-xx; covered by TCOND-22, TCOND-23 |
| NFR-01.c | None | DT-002 | GAP: review-only, no test condition (A-15) |
| NFR-02.a/b/c | None | DT-002; all test stories | GAP: no TC-xx; covered by TCOND-14, TCOND-17, TCOND-22 |
| TR-01 Unit | TC-02, TC-18, TC-21 | DT-002 | Covered |
| TR-01 API / Smoke / Performance | TC-02, TC-18, TC-21 (API) | DT-005, DT-007, DT-014 | Out of scope for DT-002 |
| TR-02 TC-03, TC-20 | n/a | DT-003 | Out of scope (FAIL flow) |
| TR-02 TC-04 to TC-17, TC-19, TC-22 | n/a | DT-004 to DT-007 | Out of scope (validation/HTTP); unit-level boundary extras in A-12 |
| Regression with DT-003 | n/a | DT-002, DT-003 | Covered by TCOND-25 |

## 5. Proposed acceptance criteria

DT-002 has ACs for FR-03.a-g, FR-06.a and FR-03.i. Added criteria for gaps:

- **FR-03.h:** **Given** any valid `PASS` input, **when** `simulate` is called, **then** the result contains exactly the documented fields (`product_id`, `status`, `stations`, `total_simulated_time_seconds`) and each station contains `station`, `status`, `duration_seconds`, with station order unchanged across calls (pending A-08).
- **FR-03.i / NFR-02.c:** **Given** `time.sleep` and `asyncio.sleep` are patched to fail, **when** `simulate` is called with assembly 300 and packaging 120, **then** a result is returned and no sleep was called.
- **FR-03.g (boundary, ASSUMPTION):** **Given** `(1, PASS, 1)`, `(300, PASS, 120)`, `(1, PASS, 120)` or `(300, PASS, 1)`, **then** totals are 2, 420, 121 and 301 and Inspection duration is 0.
- **FR-06.b:** **Given** the simulator module, **when** its imports are scanned, **then** no random, wall-clock, network or cloud-SDK module is imported.
- **NFR-01.a / NFR-02.a:** **Given** the simulator module, **when** it is imported in a clean interpreter, **then** it imports no FastAPI/API-layer module and needs no HTTP server.
- **NFR-01.b:** **Given** the simulator module, **when** the type checker runs, **then** `simulate` and the result model are fully annotated with no errors.
- **NFR-02.b:** **Given** no `AWS_*` environment variables, **when** the DT-002 tests run, **then** they pass.
- **Regression:** **Given** DT-003 is implemented, **when** the DT-002 tests are re-run, **then** they pass unchanged.

## 6. Validation checklist

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Every FR, NFR, TR in scope appears in the traceability table with a test condition or "no coverage" flag | Pass | FR-03, FR-06, NFR-01, NFR-02, TR-01 covered; gaps flagged (FR-03.h, FR-03.i, FR-06.b, NFR-01, NFR-02 have no TC-xx; NFR-01.c is review-only). |
| 2 | FR-02 boundaries have min/max/below/above conditions | N/A | Below-min and above-max are validation (DT-004); the simulator assumes valid input (SC-01). Valid min/max values are covered by TCOND-09 to TCOND-11 and TCOND-13 (A-12). |
| 3 | FR-05 categories map to HTTP 400 and the FR-07 error structure | N/A | Validation and HTTP are not in DT-002 scope (DT-004, DT-006). |
| 4 | Expected totals are correct | Pass | PASS total = `assembly_time_seconds + packaging_time_seconds` (e.g. 30 + 10 = 40; 300 + 120 = 420). The FAIL total (= `assembly_time_seconds`, Packaging skipped) is N/A here: DT-003. |
| 5 | Each finding cites a source ID, each ambiguity has a question, each assumption is labeled | Pass | A-01 to A-17 cite sources and carry questions; assumptions marked `ASSUMPTION`. |
| 6 | No condition relies on real-time sleeps, random data, or AWS credentials (NFR-02) | Pass | TCOND-14 patches sleep to fail if called; TCOND-17 runs without AWS variables. TCOND-15 is an optional wall-clock sanity check and not a primary assertion (A-14). |
| 7 | Every conflict between `docs/` and `copilot-instructions.md` is listed with its resolution | Pass | A-01, A-02, A-16 (structure/tooling from instructions); A-03 to A-07, A-17 (instruction-only items, no conditions derived). |
