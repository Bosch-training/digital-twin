"""Fixed three-station assembly-line simulation (PASS flow).

Stations always run in the order Assembly, Inspection, Packaging. Time is simulated
arithmetic in seconds; nothing sleeps or reads a clock.
"""

from dataclasses import dataclass

ASSEMBLY = "Assembly"
INSPECTION = "Inspection"
PACKAGING = "Packaging"

COMPLETED = "COMPLETED"
PASS = "PASS"


@dataclass(frozen=True)
class StationResult:
    """Outcome of one station.

    Attributes:
        station: Station name.
        status: Station status, e.g. ``COMPLETED`` or ``PASS``.
        duration_seconds: Simulated time spent at the station.
    """

    station: str
    status: str
    duration_seconds: int


@dataclass(frozen=True)
class SimulationResult:
    """Outcome of simulating one product through the line.

    Attributes:
        product_id: Product identifier, echoed unchanged.
        status: Overall status.
        stations: Station outcomes in processing order.
        total_simulated_time_seconds: Sum of all station durations.
    """

    product_id: str
    status: str
    stations: tuple[StationResult, ...]
    total_simulated_time_seconds: int


def simulate(
    product_id: str,
    assembly_time_seconds: int,
    inspection_result: str,
    packaging_time_seconds: int,
) -> SimulationResult:
    """Simulate a product on the line for the PASS path.

    Inputs are assumed valid; validation and the FAIL flow are out of scope here.

    Args:
        product_id: Product identifier.
        assembly_time_seconds: Assembly duration in seconds.
        inspection_result: Inspection outcome (``PASS``).
        packaging_time_seconds: Packaging duration in seconds.

    Returns:
        The overall result with one entry per station.
    """
    stations = (
        StationResult(ASSEMBLY, COMPLETED, assembly_time_seconds),
        StationResult(INSPECTION, inspection_result, 0),
        StationResult(PACKAGING, COMPLETED, packaging_time_seconds),
    )
    return SimulationResult(
        product_id=product_id,
        status=COMPLETED,
        stations=stations,
        total_simulated_time_seconds=sum(s.duration_seconds for s in stations),
    )
