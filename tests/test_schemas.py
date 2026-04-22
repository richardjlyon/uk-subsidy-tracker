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
