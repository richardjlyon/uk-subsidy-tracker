"""Validate raw-source pandera schemas via the public loaders + derived Parquet.

Phase 2 pre-Parquet scaffolding + Phase 4 Parquet-variant tests (D-19).

Each raw-CSV test calls a loader (which runs `schema.validate(df)`
internally) and asserts the result is non-empty with the expected key
columns. A SchemaError from pandera is raised by the loader and fails the
test automatically.

Phase-4 formal TEST-02: each derived Parquet grain is rebuilt into a
module-scoped tmp dir, then each row is validated against the Pydantic
row model declared in `uk_subsidy_tracker.schemas.cfd`. Column order is
asserted to match the model's field declaration order (D-10).
"""

from pathlib import Path

import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.data import (
    load_elexon_prices_daily,
    load_elexon_wind_daily,
    load_gas_price,
    load_lccc_dataset,
)
from uk_subsidy_tracker.schemas import (
    AnnualSummaryRow,
    ByAllocationRoundRow,
    ByTechnologyRow,
    ForwardProjectionRow,
    StationMonthRow,
)
from uk_subsidy_tracker.schemas.ro import (
    RoAnnualSummaryRow,
    RoByAllocationRoundRow,
    RoByTechnologyRow,
    RoForwardProjectionRow,
    RoStationMonthRow,
)
from uk_subsidy_tracker.schemes import cfd


def test_lccc_generation_schema():
    """LCCC CfD generation CSV matches `lccc_generation_schema`."""
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    assert not df.empty
    assert "Settlement_Date" in df.columns
    assert "CFD_Payments_GBP" in df.columns
    assert df["Settlement_Date"].dtype.kind == "M"  # datetime64
    assert df["CFD_Payments_GBP"].dtype.kind == "f"  # float


def test_lccc_portfolio_schema():
    """LCCC portfolio CSV matches `lccc_portfolio_schema`."""
    df = load_lccc_dataset("CfD Contract Portfolio Status")
    assert not df.empty
    assert "CFD_ID" in df.columns
    assert "Technology_Type" in df.columns


def test_elexon_wind_daily_schema():
    """Elexon AGWS raw CSV validates and aggregates to daily wind MW."""
    df = load_elexon_wind_daily()
    assert not df.empty
    assert "date" in df.columns
    assert "wind_mw" in df.columns
    assert df["date"].dtype.kind == "M"
    assert df["wind_mw"].dtype.kind == "f"


def test_elexon_prices_daily_schema():
    """Elexon system-prices raw CSV validates and aggregates to daily avg."""
    df = load_elexon_prices_daily()
    assert not df.empty
    assert "date" in df.columns
    assert "price_gbp_per_mwh" in df.columns
    assert df["date"].dtype.kind == "M"
    assert df["price_gbp_per_mwh"].dtype.kind == "f"


def test_ons_gas_schema():
    """ONS SAP gas XLSX validates to the documented 2-column shape."""
    df = load_gas_price()
    assert not df.empty
    assert "date" in df.columns
    assert "gas_p_per_kwh" in df.columns
    assert df["date"].dtype.kind == "M"
    assert df["gas_p_per_kwh"].dtype.kind == "f"


# ---------------------------------------------------------------------------
# Phase-4 formal TEST-02 (D-19): Parquet-variant schema validation.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def derived_dir(tmp_path_factory) -> Path:
    """Rebuild all five CfD grains once for the module (reused across tests)."""
    out = tmp_path_factory.mktemp("test-schemas-derived")
    cfd.rebuild_derived(output_dir=out)
    return out


_GRAIN_MODELS = {
    "station_month": StationMonthRow,
    "annual_summary": AnnualSummaryRow,
    "by_technology": ByTechnologyRow,
    "by_allocation_round": ByAllocationRoundRow,
    "forward_projection": ForwardProjectionRow,
}


@pytest.mark.parametrize("grain, model", list(_GRAIN_MODELS.items()))
def test_parquet_grain_schema(grain, model, derived_dir):
    """TEST-02 (D-19): each derived Parquet validates row-by-row against its Pydantic schema."""
    path = derived_dir / f"{grain}.parquet"
    assert path.exists(), f"{path} missing — cfd.rebuild_derived did not emit"
    df = pq.read_table(path).to_pandas()
    assert not df.empty, f"{grain}.parquet is empty"

    # Column set + order must match the model exactly (D-10).
    expected_columns = list(model.model_fields.keys())
    assert list(df.columns) == expected_columns, (
        f"{grain} column order/set mismatch: "
        f"expected {expected_columns}, got {list(df.columns)}"
    )

    # Validate every row. All five CfD grains are small (<20k rows) — the
    # per-row Pydantic validation completes in <1s each for this project.
    for row in df.to_dict(orient="records"):
        model.model_validate(row)


# ===========================================================================
# RO parametrised schema tests (Plan 05-10; mirrors CfD block above).
#
# Per PATTERNS.md directive, RO uses an INDEPENDENT module-scoped fixture
# (`ro_derived_dir`) and a separate `_RO_GRAIN_MODELS` dict. CfD + RO are NOT
# merged into one parametrisation — keeps shared-fixture contention away and
# allows the two schemes' rebuild costs to amortise independently.
# ===========================================================================


@pytest.fixture(scope="module")
def ro_derived_dir(tmp_path_factory) -> Path:
    """Rebuild all five RO grains once for the module (reused across tests)."""
    from uk_subsidy_tracker.schemes import ro

    out = tmp_path_factory.mktemp("test-schemas-ro-derived")
    ro.rebuild_derived(output_dir=out)
    return out


_RO_GRAIN_MODELS = [
    pytest.param("station_month", RoStationMonthRow, marks=pytest.mark.dormant),
    pytest.param("annual_summary", RoAnnualSummaryRow),
    pytest.param("by_technology", RoByTechnologyRow),
    pytest.param("by_allocation_round", RoByAllocationRoundRow, marks=pytest.mark.dormant),
    pytest.param("forward_projection", RoForwardProjectionRow, marks=pytest.mark.dormant),
]


@pytest.mark.parametrize("grain, model", _RO_GRAIN_MODELS)
def test_ro_parquet_grain_schema(grain, model, ro_derived_dir):
    """RO-03 / TEST-02: every RO Parquet grain conforms to its Pydantic row model.

    Column set + order is asserted unconditionally (D-10 Parquet column-order
    contract is meaningful even on empty data — schema lives in the file
    header). Per-row Pydantic validation skips on empty Parquets to remain
    green under the seed-stub raw inputs that ship with the repo; once real
    Ofgem RER data lands the rows are validated automatically.
    """
    path = ro_derived_dir / f"{grain}.parquet"
    assert path.exists(), (
        f"RO {grain}.parquet missing — check ro.rebuild_derived output"
    )

    df = pq.read_table(path).to_pandas()

    # Column-order discipline: Parquet columns MUST equal model field
    # declaration order (D-10). Valid against empty data — column metadata
    # is a header-level contract.
    expected_cols = list(model.model_fields.keys())
    assert list(df.columns) == expected_cols, (
        f"{grain} Parquet column order {list(df.columns)} != model field "
        f"order {expected_cols} — requires CHANGES.md ## Methodology versions "
        f"entry (D-10)"
    )

    if len(df) == 0:
        pytest.skip(
            f"RO {grain}.parquet is empty (seed-stub data); per-row schema "
            f"validation deferred until real RER data is wired"
        )

    # Validate each row via the Pydantic model.
    for row in df.to_dict(orient="records"):
        model.model_validate(row)


# ===========================================================================
# RO aggregate-grain nullability tests (Plan 05.2-03 Task 1 — D-04).
# ===========================================================================


def test_ro_annual_summary_row_eroc_nullable():
    """D-04: ro_cost_gbp_eroc must accept None under aggregate grain (Phase 05.2)."""
    from uk_subsidy_tracker.schemas.ro import RoAnnualSummaryRow
    row = RoAnnualSummaryRow(
        year=2020,
        country="GB",
        ro_generation_mwh=100.0,
        ro_cost_gbp=50.0,
        ro_cost_gbp_eroc=None,
        gas_counterfactual_gbp=30.0,
        premium_gbp=20.0,
        mutualisation_gbp=None,
        methodology_version="0.1.0",
    )
    assert row.ro_cost_gbp_eroc is None


def test_ro_annual_summary_row_eroc_still_accepts_float():
    """Backward compat — non-null eroc still valid."""
    from uk_subsidy_tracker.schemas.ro import RoAnnualSummaryRow
    row = RoAnnualSummaryRow(
        year=2020, country="GB",
        ro_generation_mwh=100.0, ro_cost_gbp=50.0,
        ro_cost_gbp_eroc=45.0, gas_counterfactual_gbp=30.0,
        premium_gbp=20.0, mutualisation_gbp=None,
        methodology_version="0.1.0",
    )
    assert row.ro_cost_gbp_eroc == 45.0


def test_ro_by_technology_row_eroc_nullable():
    """D-04: by_technology also gets nullable eroc."""
    from uk_subsidy_tracker.schemas.ro import RoByTechnologyRow
    row = RoByTechnologyRow(
        year=2020, technology="Offshore wind",
        ro_generation_mwh=100.0, ro_cost_gbp=50.0,
        ro_cost_gbp_eroc=None,
        methodology_version="0.1.0",
    )
    assert row.ro_cost_gbp_eroc is None


# ===========================================================================
# Plan 06-01 — Portal cross-scheme parquet schema conformance (TEST-02 / D-19).
#
# Independent module-scoped fixture rebuilds CfD + RO into the project derived
# tree (cross_scheme_model reads from PROJECT_ROOT) AND emits cross_scheme.parquet
# into a tmp dir. CrossSchemeRow column-order discipline (D-10) + per-row
# Pydantic validation. NaN handling: households_uk may be NaN for pre-2014
# RO years (RESEARCH Q3 — pre-2014 X3 bars omitted) — those rows are skipped
# so Pydantic int validation does not fail. generation_mwh may be NaN for
# pre-SY18 RO — the field is Optional so coerce NaN→None.
# ===========================================================================


from uk_subsidy_tracker.schemas.portal import CrossSchemeRow  # noqa: E402

_PORTAL_GRAIN_MODELS = {"cross_scheme": CrossSchemeRow}


@pytest.fixture(scope="module")
def portal_derived_dir(tmp_path_factory) -> Path:
    from uk_subsidy_tracker.schemes import cfd, portal, ro
    out = tmp_path_factory.mktemp("test-schemas-portal-derived")
    cfd.rebuild_derived()
    ro.rebuild_derived()
    portal.rebuild_derived(output_dir=out)
    return out


@pytest.mark.parametrize("grain, model", list(_PORTAL_GRAIN_MODELS.items()))
def test_portal_parquet_grain_schema(grain, model, portal_derived_dir):
    """TEST-02 / D-19: cross_scheme.parquet conforms to CrossSchemeRow.

    Column-order discipline (D-10) + per-row Pydantic validation. Rows with
    NaN ``households_uk`` (pre-2014 RO years per RESEARCH Q3) are skipped —
    the X3 plotting layer filters them; row-level int validation cannot run
    on NaN.
    """
    import math
    path = portal_derived_dir / f"{grain}.parquet"
    assert path.exists(), f"{grain}.parquet missing — portal.rebuild_derived did not emit"
    df = pq.read_table(path).to_pandas()
    expected_columns = list(model.model_fields.keys())
    assert list(df.columns) == expected_columns, (
        f"{grain} column order drift: got {list(df.columns)} "
        f"vs expected {expected_columns}"
    )
    for row in df.to_dict(orient="records"):
        # households_uk may be NaN for years pre-2014 (RESEARCH Q3 — pre-2014
        # X3 bars omitted). The CrossSchemeRow households_uk: int field cannot
        # accept NaN, so skip those rows. The X3 chart filters them at render time.
        h = row.get("households_uk")
        if h is None or (isinstance(h, float) and math.isnan(h)):
            continue
        # generation_mwh may also be NaN for pre-SY18 RO; the field is Optional
        # so coerce NaN→None for Pydantic validation.
        g = row.get("generation_mwh")
        if isinstance(g, float) and math.isnan(g):
            row["generation_mwh"] = None
        model.model_validate(row)
