"""Pydantic row schemas for the derived Parquet layer.

Field declaration order on each row model IS the canonical column order
(D-10). Every model emits JSON Schema via `model_json_schema(mode='serialization')`
for the per-table `<grain>.schema.json` sidecars (D-11, built in Plan 04).
"""
from uk_subsidy_tracker.schemas.cfd import (
    AnnualSummaryRow,
    ByAllocationRoundRow,
    ByTechnologyRow,
    ForwardProjectionRow,
    StationMonthRow,
    emit_schema_json,
)

__all__ = [
    "StationMonthRow",
    "AnnualSummaryRow",
    "ByTechnologyRow",
    "ByAllocationRoundRow",
    "ForwardProjectionRow",
    "emit_schema_json",
]
