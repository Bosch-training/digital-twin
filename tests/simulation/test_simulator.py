"""Unit tests for DT-002: simulator PASS flow.

Sources: docs/test-spec/DT-002-test-spec.csv, docs/dt-002-analysis.md, docs/DT-002.md,
docs/digital_twin_assembly_line_testing_requirements.md (FR-03, FR-06, NFR-01, NFR-02).
"""

import ast
import asyncio
import dataclasses
import inspect
import subprocess
import sys
import time
import typing
from pathlib import Path

import pytest

from digital_twin.simulation.simulator import simulate

ROOT = Path(__file__).resolve().parents[2]
SIMULATOR_SOURCE = ROOT / "src" / "digital_twin" / "simulation" / "simulator.py"

PRODUCT_ID = "PROD-001"
AWS_VARIABLES = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_PROFILE",
    "AWS_DEFAULT_REGION",
    "AWS_REGION",
)
FORBIDDEN_IMPORTS = {
    "time",
    "random",
    "datetime",
    "asyncio",
    "socket",
    "os",
    "boto3",
    "requests",
    "httpx",
    "simpy",
}
API_MODULE_CHECK = """
import sys
import digital_twin.simulation.simulator
FORBIDDEN = ("fastapi", "starlette", "digital_twin.api", "app")
for name in sorted(sys.modules):
    if any(name == prefix or name.startswith(prefix + ".") for prefix in FORBIDDEN):
        print(name)
"""


def _assert_fr03_example(result) -> None:
    assert result.product_id == PRODUCT_ID
    assert result.status == "COMPLETED"
    assert [(s.station, s.status, s.duration_seconds) for s in result.stations] == [
        ("Assembly", "COMPLETED", 30),
        ("Inspection", "PASS", 0),
        ("Packaging", "COMPLETED", 10),
    ]
    assert result.total_simulated_time_seconds == 40


# TS-DT002-01
def test_simulate_pass_flow_returns_completed_and_echoes_product_id():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert result.status == "COMPLETED"
    assert result.product_id == PRODUCT_ID
    assert len(result.stations) == 3


# TS-DT002-02
def test_simulate_pass_flow_runs_three_stations_in_order():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert [s.station for s in result.stations] == ["Assembly", "Inspection", "Packaging"]


# TS-DT002-03
def test_simulate_pass_flow_station_statuses_in_order():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert [s.status for s in result.stations] == ["COMPLETED", "PASS", "COMPLETED"]


# TS-DT002-04, TS-DT002-09 to TS-DT002-12
@pytest.mark.parametrize(
    ("assembly_time_s", "packaging_time_s", "expected_durations", "expected_total_s"),
    [
        pytest.param(30, 10, [30, 0, 10], 40, id="TS-DT002-04"),
        pytest.param(1, 1, [1, 0, 1], 2, id="TS-DT002-09"),
        pytest.param(300, 120, [300, 0, 120], 420, id="TS-DT002-10"),
        pytest.param(1, 120, [1, 0, 120], 121, id="TS-DT002-11-A"),
        pytest.param(300, 1, [300, 0, 1], 301, id="TS-DT002-11-B"),
        pytest.param(120, 5, [120, 0, 5], 125, id="TS-DT002-12-A"),
        pytest.param(5, 120, [5, 0, 120], 125, id="TS-DT002-12-B"),
    ],
)
def test_simulate_station_durations_and_total_follow_inputs(
    assembly_time_s, packaging_time_s, expected_durations, expected_total_s
):
    result = simulate(PRODUCT_ID, assembly_time_s, "PASS", packaging_time_s)

    assert [s.duration_seconds for s in result.stations] == expected_durations
    assert result.total_simulated_time_seconds == expected_total_s


# TS-DT002-05
def test_simulate_total_is_assembly_plus_packaging_time():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert result.total_simulated_time_seconds == 40


# TS-DT002-06
def test_simulate_result_matches_fr03_example_response():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    _assert_fr03_example(result)


# TS-DT002-07
def test_simulate_result_exposes_only_documented_fields():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)
    station = result.stations[0]

    assert {f.name for f in dataclasses.fields(result)} == {
        "product_id",
        "status",
        "stations",
        "total_simulated_time_seconds",
    }
    # ASSUMPTION: A-08 station entries use the same attribute-access style as the result.
    assert {f.name for f in dataclasses.fields(station)} == {
        "station",
        "status",
        "duration_seconds",
    }
    assert not hasattr(result, "reason")


# TS-DT002-08
def test_simulate_durations_and_total_are_integers():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)
    values = [s.duration_seconds for s in result.stations]
    values.append(result.total_simulated_time_seconds)

    assert all(isinstance(v, int) and not isinstance(v, bool) for v in values)


# TS-DT002-13
@pytest.mark.parametrize(
    "product_id",
    [
        pytest.param("A", id="TS-DT002-13-A"),
        pytest.param("P" * 50, id="TS-DT002-13-B"),
        pytest.param(" PROD-001 ", id="TS-DT002-13-C"),
    ],
)
def test_simulate_echoes_product_id_unchanged(product_id):
    result = simulate(product_id, 30, "PASS", 10)

    assert result.product_id == product_id


# TS-DT002-14
def test_simulate_long_assembly_does_not_sleep(monkeypatch):
    def fail_sleep(*_args, **_kwargs):
        raise AssertionError("simulate must not sleep")

    monkeypatch.setattr(time, "sleep", fail_sleep)
    monkeypatch.setattr(asyncio, "sleep", fail_sleep)

    result = simulate(PRODUCT_ID, 300, "PASS", 120)

    assert result.status == "COMPLETED"


# TS-DT002-16
def test_simulator_module_imports_no_clock_random_network_or_cloud_modules():
    tree = ast.parse(SIMULATOR_SOURCE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.add(node.module.split(".")[0])

    assert not imported & FORBIDDEN_IMPORTS


# TS-DT002-17
def test_simulate_needs_no_aws_credentials(monkeypatch):
    for name in AWS_VARIABLES:
        monkeypatch.delenv(name, raising=False)

    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    _assert_fr03_example(result)


# TS-DT002-18
def test_simulate_identical_input_twice_gives_equal_results():
    first = simulate(PRODUCT_ID, 30, "PASS", 10)
    second = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert first == second


# TS-DT002-19
def test_simulate_100_identical_calls_give_equal_results():
    first = simulate(PRODUCT_ID, 30, "PASS", 10)

    results = [simulate(PRODUCT_ID, 30, "PASS", 10) for _ in range(100)]

    assert all(r == first for r in results)


# TS-DT002-20
def test_simulate_calls_do_not_leak_state():
    first = simulate(PRODUCT_ID, 30, "PASS", 10)
    other = simulate("PROD-002", 300, "PASS", 120)
    third = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert third == first
    assert other.product_id == "PROD-002"
    assert [s.duration_seconds for s in other.stations] == [300, 0, 120]
    assert other.total_simulated_time_seconds == 420
    assert other != first


# TS-DT002-21
def test_simulate_mutating_returned_stations_does_not_affect_later_calls():
    first = simulate(PRODUCT_ID, 30, "PASS", 10)
    # ASSUMPTION: A-08 the stations container may be a list or a tuple; mutate only a list.
    if isinstance(first.stations, list):
        first.stations.clear()

    second = simulate(PRODUCT_ID, 30, "PASS", 10)

    _assert_fr03_example(second)


# TS-DT002-22
def test_simulate_result_is_frozen_dataclass():
    result = simulate(PRODUCT_ID, 30, "PASS", 10)

    assert dataclasses.is_dataclass(result)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.status = "REJECTED"
    assert result.status == "COMPLETED"


# TS-DT002-23
def test_simulator_module_does_not_import_api_layer():
    completed = subprocess.run(
        [sys.executable, "-c", API_MODULE_CHECK],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == ""


# TS-DT002-24
def test_simulate_and_result_models_are_fully_annotated():
    signature = inspect.signature(simulate)

    assert list(signature.parameters) == [
        "product_id",
        "assembly_time_seconds",
        "inspection_result",
        "packaging_time_seconds",
    ]
    for parameter in signature.parameters.values():
        assert parameter.annotation is not inspect.Parameter.empty
    assert signature.return_annotation is not inspect.Signature.empty

    result = simulate(PRODUCT_ID, 30, "PASS", 10)
    for model in (type(result), type(result.stations[0])):
        hints = typing.get_type_hints(model)
        assert {f.name for f in dataclasses.fields(model)} <= set(hints)


# TS-DT002-27
@pytest.mark.parametrize(
    ("assembly_time_s", "packaging_time_s"),
    [
        pytest.param(30, 10, id="TS-DT002-27-30-10"),
        pytest.param(1, 1, id="TS-DT002-27-1-1"),
        pytest.param(300, 120, id="TS-DT002-27-300-120"),
        pytest.param(1, 120, id="TS-DT002-27-1-120"),
        pytest.param(300, 1, id="TS-DT002-27-300-1"),
        pytest.param(120, 5, id="TS-DT002-27-120-5"),
        pytest.param(5, 120, id="TS-DT002-27-5-120"),
    ],
)
def test_simulate_total_equals_sum_of_durations_and_inspection_is_zero(
    assembly_time_s, packaging_time_s
):
    result = simulate(PRODUCT_ID, assembly_time_s, "PASS", packaging_time_s)
    durations = [s.duration_seconds for s in result.stations]

    assert result.total_simulated_time_seconds == assembly_time_s + packaging_time_s
    assert result.total_simulated_time_seconds == sum(durations)
    assert durations[1] == 0
