"""Validate raw-source pandera schemas via the public loaders.

Phase 2 pre-Parquet scaffolding for TEST-02. Each test calls a loader
(which runs `schema.validate(df)` internally) and asserts the result is
non-empty with the expected key columns. A SchemaError from pandera is
raised by the loader and fails the test automatically — we do not need
to import pandera here.

Formal TEST-02 is satisfied in Phase 4 when Parquet-schema assertions
are added to this same file.
"""

from uk_subsidy_tracker.data import (
    load_elexon_prices_daily,
    load_elexon_wind_daily,
    load_gas_price,
    load_lccc_dataset,
)


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
