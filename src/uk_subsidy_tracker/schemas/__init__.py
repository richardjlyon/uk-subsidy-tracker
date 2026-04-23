"""Pydantic row schemas for the derived Parquet layer.

Field declaration order on each row model IS the canonical column order
(D-10). Every model emits JSON Schema via `model_json_schema(mode='serialization')`
for the per-table `<grain>.schema.json` sidecars (D-11, built in Plan 04).

``emit_schema_json`` is declared in ``schemas.cfd`` and is scheme-agnostic;
``schemas.ro`` imports (not re-declares) it so the emitter upgrade is atomic
across schemes.
"""
from uk_subsidy_tracker.schemas.cfd import (
    AnnualSummaryRow,
    ByAllocationRoundRow,
    ByTechnologyRow,
    ForwardProjectionRow,
    StationMonthRow,
    emit_schema_json,
)
from uk_subsidy_tracker.schemas.ro import (
    RoAnnualSummaryRow,
    RoByAllocationRoundRow,
    RoByTechnologyRow,
    RoForwardProjectionRow,
    RoStationMonthRow,
)

__all__ = [
    # CfD row models (Plan 02-02).
    "StationMonthRow",
    "AnnualSummaryRow",
    "ByTechnologyRow",
    "ByAllocationRoundRow",
    "ForwardProjectionRow",
    # RO row models (Plan 05-03).
    "RoStationMonthRow",
    "RoAnnualSummaryRow",
    "RoByTechnologyRow",
    "RoByAllocationRoundRow",
    "RoForwardProjectionRow",
    # Scheme-agnostic emitter (DRY-shared via schemas.cfd).
    "emit_schema_json",
]
