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


# ===========================================================================
# RO row-conservation tests (Plan 05-10; TEST-03; D-09 country groupby).
#
# Per PATTERNS.md directive, RO uses INDEPENDENT module-scoped fixtures
# (`ro_derived_dir`, `ro_station_month`, etc.) and does NOT merge into the
# CfD parametrisation. Annual rollup uses (year, country) per D-09 because
# annual_summary emits one row per (year, country) tuple — NOT one per year.
# ===========================================================================


@pytest.fixture(scope="module")
def ro_derived_dir(tmp_path_factory) -> Path:
    from uk_subsidy_tracker.schemes import ro

    out = tmp_path_factory.mktemp("test-aggregates-ro-derived")
    ro.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def ro_station_month(ro_derived_dir) -> pd.DataFrame:
    df = pq.read_table(ro_derived_dir / "station_month.parquet").to_pandas()
    # int64 to match the year dtype declared by Ro*Row models (D-10).
    # `dt.year` returns int32 by default — cast explicitly.
    df["year"] = df["month_end"].dt.year.astype("int64")
    return df


@pytest.fixture(scope="module")
def ro_annual_summary(ro_derived_dir) -> pd.DataFrame:
    return pq.read_table(ro_derived_dir / "annual_summary.parquet").to_pandas()


@pytest.fixture(scope="module")
def ro_by_technology(ro_derived_dir) -> pd.DataFrame:
    return pq.read_table(ro_derived_dir / "by_technology.parquet").to_pandas()


@pytest.fixture(scope="module")
def ro_by_allocation_round(ro_derived_dir) -> pd.DataFrame:
    return pq.read_table(ro_derived_dir / "by_allocation_round.parquet").to_pandas()


def _skip_if_empty_ro_station_month(df: pd.DataFrame) -> None:
    """D-11 fallback: skip RO row-conservation when stub data is empty.

    pandas ``assert_series_equal`` rejects empty MultiIndex levels because
    ``inferred_type`` differs between an empty groupby result (carries the
    column dtype, e.g. 'string') and an empty ``set_index`` MultiIndex
    (reports 'empty'). Same shape, different metadata.

    The row-conservation contract is meaningful only on non-empty data;
    the test re-activates the moment the seed-stub raw inputs are replaced
    with a single non-empty Ofgem RER fetch.
    """
    if len(df) == 0:
        pytest.skip(
            "RO station_month is empty (seed-stub raw data); row-conservation "
            "invariant deferred until real RER data is wired"
        )


@pytest.mark.dormant
def test_ro_annual_vs_station_month_parquet(ro_station_month, ro_annual_summary):
    """RO-03 / TEST-03: annual_summary.ro_cost_gbp = sum(station_month) per (year, country).

    D-09: annual_summary emits one row per (year, country) tuple, so the
    row-conservation invariant is groupby year+country (NOT year alone).

    DORMANT: requires station_month.parquet from ro-register.xlsx (Option-D deferred).
    Re-activate on backlog 999.1.
    """
    _skip_if_empty_ro_station_month(ro_station_month)
    from_sm = (
        ro_station_month.groupby(["year", "country"], observed=True)["ro_cost_gbp"]
        .sum()
        .sort_index()
    )
    from_annual = (
        ro_annual_summary.set_index(["year", "country"])["ro_cost_gbp"].sort_index()
    )
    pd.testing.assert_series_equal(from_sm, from_annual, check_names=False)


@pytest.mark.dormant
def test_ro_by_technology_vs_station_month_parquet(ro_station_month, ro_by_technology):
    """TEST-03: by_technology.ro_cost_gbp = sum(station_month) per (year, technology).

    DORMANT: requires station_month.parquet from ro-register.xlsx (Option-D deferred).
    Re-activate on backlog 999.1.
    """
    _skip_if_empty_ro_station_month(ro_station_month)
    from_sm = (
        ro_station_month.groupby(["year", "technology"], observed=True)["ro_cost_gbp"]
        .sum()
        .sort_index()
    )
    from_by_tech = (
        ro_by_technology.set_index(["year", "technology"])["ro_cost_gbp"].sort_index()
    )
    pd.testing.assert_series_equal(from_sm, from_by_tech, check_names=False)


@pytest.mark.dormant
def test_ro_by_allocation_round_vs_station_month_parquet(
    ro_station_month, ro_by_allocation_round
):
    """TEST-03: by_allocation_round.ro_cost_gbp = sum(station_month) per (year, commissioning_window).

    RO has no allocation-round axis (unlike CfD); ``commissioning_window``
    serves as the banding-cohort axis per RESEARCH §5.

    DORMANT: requires station_month.parquet from ro-register.xlsx (Option-D deferred).
    Re-activate on backlog 999.1.
    """
    _skip_if_empty_ro_station_month(ro_station_month)
    from_sm = (
        ro_station_month.groupby(["year", "commissioning_window"], observed=True)[
            "ro_cost_gbp"
        ]
        .sum()
        .sort_index()
    )
    from_by_round = (
        ro_by_allocation_round.set_index(["year", "commissioning_window"])[
            "ro_cost_gbp"
        ].sort_index()
    )
    pd.testing.assert_series_equal(from_sm, from_by_round, check_names=False)
