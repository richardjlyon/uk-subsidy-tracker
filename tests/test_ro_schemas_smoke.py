"""Smoke tests for the RO Pydantic row schemas (Plan 05-03).

Every test is a D-10 tripwire: field declaration order IS the Parquet column
order, so each expected-field-list below is a verbatim canonical reference.
Any code change that reorders fields will also need a matching test change
and a CHANGES.md ``## Methodology versions`` entry citing D-10.

emit_schema_json is the scheme-agnostic emitter declared in schemas/cfd.py;
this suite verifies schemas/ro.py imports (and does not re-declare) it.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Canonical field-order references (D-10 tripwire). Any reorder = test + code
# + CHANGES.md ## Methodology versions entry citing D-10.
# ---------------------------------------------------------------------------

RO_STATION_MONTH_FIELDS = [
    "station_id",
    "country",
    "technology",
    "commissioning_window",
    "month_end",
    "obligation_year",
    "generation_mwh",
    "rocs_issued",
    "rocs_computed",
    "banding_factor_yaml",
    "ro_cost_gbp",
    "ro_cost_gbp_eroc",
    "ro_cost_gbp_nocarbon",
    "gas_counterfactual_gbp",
    "premium_gbp",
    "mutualisation_gbp",
    "methodology_version",
]

RO_ANNUAL_SUMMARY_FIELDS = [
    "year",
    "country",
    "ro_generation_mwh",
    "ro_cost_gbp",
    "ro_cost_gbp_eroc",
    "gas_counterfactual_gbp",
    "premium_gbp",
    "mutualisation_gbp",
    "methodology_version",
]

RO_BY_TECHNOLOGY_FIELDS = [
    "year",
    "technology",
    "ro_generation_mwh",
    "ro_cost_gbp",
    "ro_cost_gbp_eroc",
    "methodology_version",
]

RO_BY_ALLOCATION_ROUND_FIELDS = [
    "year",
    "commissioning_window",
    "ro_generation_mwh",
    "ro_cost_gbp",
    "ro_cost_gbp_eroc",
    "methodology_version",
]

RO_FORWARD_PROJECTION_FIELDS = [
    "year",
    "technology",
    "remaining_committed_mwh",
    "remaining_cost_gbp",
    "station_count_active",
    "avg_banding_factor",
    "methodology_version",
]


# ---------------------------------------------------------------------------
# Field-order tests (5) — D-10 tripwire.
# ---------------------------------------------------------------------------


def test_ro_station_month_row_field_order() -> None:
    from uk_subsidy_tracker.schemas.ro import RoStationMonthRow

    assert list(RoStationMonthRow.model_fields.keys()) == RO_STATION_MONTH_FIELDS


def test_ro_annual_summary_row_field_order() -> None:
    from uk_subsidy_tracker.schemas.ro import RoAnnualSummaryRow

    assert list(RoAnnualSummaryRow.model_fields.keys()) == RO_ANNUAL_SUMMARY_FIELDS


def test_ro_by_technology_row_field_order() -> None:
    from uk_subsidy_tracker.schemas.ro import RoByTechnologyRow

    assert list(RoByTechnologyRow.model_fields.keys()) == RO_BY_TECHNOLOGY_FIELDS


def test_ro_by_allocation_round_row_field_order() -> None:
    from uk_subsidy_tracker.schemas.ro import RoByAllocationRoundRow

    assert (
        list(RoByAllocationRoundRow.model_fields.keys())
        == RO_BY_ALLOCATION_ROUND_FIELDS
    )


def test_ro_forward_projection_row_field_order() -> None:
    from uk_subsidy_tracker.schemas.ro import RoForwardProjectionRow

    assert (
        list(RoForwardProjectionRow.model_fields.keys())
        == RO_FORWARD_PROJECTION_FIELDS
    )


# ---------------------------------------------------------------------------
# Instantiation + nullability tests.
# ---------------------------------------------------------------------------


def _station_month_kwargs(**overrides: object) -> dict[str, object]:
    """Minimal valid kwargs for RoStationMonthRow (Plan 05-05 column set)."""
    base: dict[str, object] = {
        "station_id": "RO-000001",
        "country": "GB",
        "technology": "Onshore Wind",
        "commissioning_window": "2013/14",
        "month_end": date(2015, 3, 31),
        "obligation_year": 2014,
        "generation_mwh": 1234.5,
        "rocs_issued": 1234.5,
        "rocs_computed": 1234.5,
        "banding_factor_yaml": 1.0,
        "ro_cost_gbp": 50000.0,
        "ro_cost_gbp_eroc": 48000.0,
        "ro_cost_gbp_nocarbon": 45000.0,
        "gas_counterfactual_gbp": 30000.0,
        "premium_gbp": 20000.0,
        "mutualisation_gbp": None,
        "methodology_version": "0.1.0",
    }
    base.update(overrides)
    return base


def test_ro_station_month_row_instantiates_with_valid_data() -> None:
    from uk_subsidy_tracker.schemas.ro import RoStationMonthRow

    row = RoStationMonthRow(**_station_month_kwargs())

    dumped = row.model_dump()
    assert list(dumped.keys()) == RO_STATION_MONTH_FIELDS
    assert dumped["country"] == "GB"
    assert dumped["methodology_version"] == "0.1.0"


def test_mutualisation_gbp_is_optional() -> None:
    from uk_subsidy_tracker.schemas.ro import RoAnnualSummaryRow, RoStationMonthRow

    # station_month: mutualisation_gbp defaults to None and accepts None.
    row_sm = RoStationMonthRow(**_station_month_kwargs(mutualisation_gbp=None))
    assert row_sm.mutualisation_gbp is None

    # station_month: accepts a numeric value (OY 2021-22 spike case).
    row_sm_spike = RoStationMonthRow(
        **_station_month_kwargs(mutualisation_gbp=12345.67)
    )
    assert row_sm_spike.mutualisation_gbp == pytest.approx(12345.67)

    # annual_summary: mutualisation_gbp must also be nullable per D-11.
    row_as = RoAnnualSummaryRow(
        year=2014,
        country="GB",
        ro_generation_mwh=1000.0,
        ro_cost_gbp=50000.0,
        ro_cost_gbp_eroc=48000.0,
        gas_counterfactual_gbp=30000.0,
        premium_gbp=20000.0,
        mutualisation_gbp=None,
        methodology_version="0.1.0",
    )
    assert row_as.mutualisation_gbp is None


# ---------------------------------------------------------------------------
# emit_schema_json re-use tripwire (T-5.03-02 mitigation).
# ---------------------------------------------------------------------------


def test_emit_schema_json_imported_not_reimplemented() -> None:
    """schemas/ro.py must import emit_schema_json from schemas.cfd, not redeclare it.

    Scheme-agnostic emitter = single source of truth per D-10 trust boundary;
    duplication here would break atomic upgrade across schemes.
    """
    ro_path = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "uk_subsidy_tracker"
        / "schemas"
        / "ro.py"
    )
    source = ro_path.read_text(encoding="utf-8")

    assert "def emit_schema_json" not in source, (
        "schemas/ro.py must NOT re-declare emit_schema_json; import it from "
        "schemas.cfd instead (scheme-agnostic, single source of truth per D-10)."
    )
    assert (
        "from uk_subsidy_tracker.schemas.cfd import emit_schema_json" in source
    ), (
        "schemas/ro.py must import emit_schema_json from schemas.cfd verbatim "
        "so the emitter is shared across schemes (T-5.03-02 mitigation)."
    )


# ---------------------------------------------------------------------------
# Barrel re-export tripwire.
# ---------------------------------------------------------------------------


def test_ro_schemas_barrel_reexport() -> None:
    """schemas/__init__.py must re-export the 5 RO row models."""
    # Importing the names from the barrel must succeed.
    from uk_subsidy_tracker.schemas import (  # noqa: F401
        RoAnnualSummaryRow,
        RoByAllocationRoundRow,
        RoByTechnologyRow,
        RoForwardProjectionRow,
        RoStationMonthRow,
    )
