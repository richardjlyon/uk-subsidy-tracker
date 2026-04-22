"""Row-conservation invariants on the CfD pipeline.

Phase 2 pre-Parquet scaffolding + Phase 4 formal TEST-03 on derived Parquet (D-20).

Scaffolding invariant: aggregating CFD_Payments_GBP by year must equal
aggregating by (year, Technology) and then collapsing back to year. A
mismatch means the groupby dropped rows — typically a NaN in the
`Technology` column.

Formal TEST-03 (D-20): after cfd.rebuild_derived(), the annual rollups
must reconcile row-for-row with the canonical station_month grain. Any
groupby NaN-swallow or off-by-one error is exposed by
`pd.testing.assert_series_equal` (exact equality).
"""

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pytest

from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.schemes import cfd


@pytest.fixture(scope="module")
def lccc_gen():
    """Load the LCCC generation CSV once per test module, derive `year`."""
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df = df.copy()
    df["year"] = df["Settlement_Date"].dt.year
    return df


def test_year_vs_year_tech_sum_match(lccc_gen):
    """TEST-03 scaffolding: no row leakage from tech decomposition."""
    by_year = lccc_gen.groupby("year")["CFD_Payments_GBP"].sum()
    by_year_tech = (
        lccc_gen.groupby(["year", "Technology"])["CFD_Payments_GBP"]
        .sum()
        .groupby("year")
        .sum()
    )
    pd.testing.assert_series_equal(
        by_year.sort_index(),
        by_year_tech.sort_index(),
        check_names=False,
    )


def test_no_orphan_technologies(lccc_gen):
    """Every row has a non-null Technology (else groupby silently drops it)."""
    assert lccc_gen["Technology"].notna().all(), (
        "LCCC generation row with null Technology detected — "
        "would silently drop from year×technology aggregation."
    )


# ---------------------------------------------------------------------------
# Phase-4 formal TEST-03 (D-20): Parquet row-conservation across grains.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def derived_dir(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("test-aggregates-derived")
    cfd.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def station_month(derived_dir) -> pd.DataFrame:
    df = pq.read_table(derived_dir / "station_month.parquet").to_pandas()
    # int64 to match the year dtype declared by AnnualSummaryRow / ByTechnologyRow
    # / ByAllocationRoundRow (D-10). `dt.year` gives int32 by default.
    df["year"] = df["month_end"].dt.year.astype("int64")
    return df


@pytest.fixture(scope="module")
def annual_summary(derived_dir) -> pd.DataFrame:
    return pq.read_table(derived_dir / "annual_summary.parquet").to_pandas()


@pytest.fixture(scope="module")
def by_technology(derived_dir) -> pd.DataFrame:
    return pq.read_table(derived_dir / "by_technology.parquet").to_pandas()


@pytest.fixture(scope="module")
def by_allocation_round(derived_dir) -> pd.DataFrame:
    return pq.read_table(derived_dir / "by_allocation_round.parquet").to_pandas()


def test_annual_vs_station_month_parquet(station_month, annual_summary):
    """TEST-03 (D-20): annual_summary.cfd_payments_gbp = sum(station_month by year)."""
    from_sm = (
        station_month.groupby("year")["cfd_payments_gbp"].sum().sort_index()
    )
    from_annual = (
        annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
    )
    pd.testing.assert_series_equal(from_sm, from_annual, check_names=False)


def test_by_tech_vs_annual_parquet(by_technology, annual_summary):
    """TEST-03 (D-20): sum(by_technology by year) = annual_summary by year."""
    from_tech = (
        by_technology.groupby("year")["cfd_payments_gbp"].sum().sort_index()
    )
    from_annual = (
        annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
    )
    pd.testing.assert_series_equal(from_tech, from_annual, check_names=False)


def test_by_round_vs_annual_parquet(by_allocation_round, annual_summary):
    """TEST-03 (D-20): sum(by_allocation_round by year) = annual_summary by year."""
    from_round = (
        by_allocation_round.groupby("year")["cfd_payments_gbp"].sum().sort_index()
    )
    from_annual = (
        annual_summary.set_index("year")["cfd_payments_gbp"].sort_index()
    )
    pd.testing.assert_series_equal(from_round, from_annual, check_names=False)
