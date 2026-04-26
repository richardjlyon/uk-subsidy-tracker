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


# ===========================================================================
# Plan 06-01 — Cross-scheme portal row-conservation tests (TEST-03 / D-20).
#
# Per PATTERNS.md directive, the portal uses INDEPENDENT module-scoped fixtures
# that rebuild CfD + RO into the *project* derived tree (the cross_scheme_model
# reads from PROJECT_ROOT-relative paths, not from `out`) and emit the portal
# parquet into `out`. Row-conservation invariant: per-scheme cost subset of
# cross_scheme.parquet must equal each scheme's annual_summary.parquet total
# to ±£1, AND per (year, scheme) row.
# ===========================================================================


from uk_subsidy_tracker import PROJECT_ROOT  # noqa: E402


@pytest.fixture(scope="module")
def portal_derived_dir(tmp_path_factory) -> Path:
    """Rebuild CfD + RO + portal once for the module."""
    from uk_subsidy_tracker.schemes import cfd, portal, ro

    out = tmp_path_factory.mktemp("test-aggregates-portal-derived")
    # cross_scheme_model reads from PROJECT_ROOT-relative paths, so refresh
    # CfD + RO derived parquets in-place in data/derived/<scheme>/ first.
    cfd.rebuild_derived()
    ro.rebuild_derived()
    portal.rebuild_derived(output_dir=out)
    return out


@pytest.fixture(scope="module")
def cross_scheme(portal_derived_dir) -> pd.DataFrame:
    return pq.read_table(portal_derived_dir / "cross_scheme.parquet").to_pandas()


def test_cross_scheme_row_conservation(cross_scheme):
    """TEST-03 / D-20: per-scheme cost subset matches source annual_summary totals.

    CfD: sum(cross_scheme[scheme=='CfD']['cost_gbp']) == sum(cfd_annual['cfd_payments_gbp'])
    RO:  sum(cross_scheme[scheme=='RO']['cost_gbp']) == sum(ro_annual_GB['ro_cost_gbp'])
         (with HAZARD #1 GB filter + HAZARD #2 NaN-cost drop)
    """
    # CfD subset row-conservation
    cfd_total_cross = float(cross_scheme[cross_scheme["scheme"] == "CfD"]["cost_gbp"].sum())
    cfd_src = pq.read_table(
        PROJECT_ROOT / "data/derived/cfd/annual_summary.parquet"
    ).to_pandas()
    cfd_total_src = float(cfd_src["cfd_payments_gbp"].sum())
    assert abs(cfd_total_cross - cfd_total_src) <= 1.0, (
        f"CfD row-conservation failed: cross=£{cfd_total_cross:,.0f} "
        f"src=£{cfd_total_src:,.0f}"
    )
    # RO subset row-conservation (GB-only, NaN-cost dropped per HAZARD #1+#2)
    ro_total_cross = float(cross_scheme[cross_scheme["scheme"] == "RO"]["cost_gbp"].sum())
    ro_src = pq.read_table(
        PROJECT_ROOT / "data/derived/ro/annual_summary.parquet"
    ).to_pandas()
    ro_src_gb = ro_src[(ro_src["country"] == "GB") & ro_src["ro_cost_gbp"].notna()]
    ro_total_src = float(ro_src_gb["ro_cost_gbp"].sum())
    assert abs(ro_total_cross - ro_total_src) <= 1.0, (
        f"RO row-conservation failed: cross=£{ro_total_cross:,.0f} "
        f"src=£{ro_total_src:,.0f}"
    )


def test_cross_scheme_per_year_conservation(cross_scheme):
    """TEST-03 / D-20: every (year, scheme) row matches its source annual_summary cell.

    Per-row conservation is the strict variant — exposes any year-mapping or
    type-coercion drift that the aggregate-totals check would mask.
    """
    cfd_src = pq.read_table(
        PROJECT_ROOT / "data/derived/cfd/annual_summary.parquet"
    ).to_pandas()
    ro_src = pq.read_table(
        PROJECT_ROOT / "data/derived/ro/annual_summary.parquet"
    ).to_pandas()
    ro_src_gb = ro_src[(ro_src["country"] == "GB") & ro_src["ro_cost_gbp"].notna()]

    cfd_lookup = dict(zip(cfd_src["year"].astype(int), cfd_src["cfd_payments_gbp"]))
    ro_lookup = dict(zip(ro_src_gb["year"].astype(int), ro_src_gb["ro_cost_gbp"]))

    for row in cross_scheme.to_dict(orient="records"):
        year = int(row["year"])
        scheme = row["scheme"]
        cross_cost = float(row["cost_gbp"])
        if scheme == "CfD":
            assert year in cfd_lookup, f"CfD year {year} missing in source annual_summary"
            assert abs(cross_cost - float(cfd_lookup[year])) <= 1.0, (
                f"CfD year={year}: cross=£{cross_cost:,.2f} "
                f"vs src=£{float(cfd_lookup[year]):,.2f}"
            )
        elif scheme == "RO":
            assert year in ro_lookup, f"RO year {year} missing in source annual_summary GB"
            assert abs(cross_cost - float(ro_lookup[year])) <= 1.0, (
                f"RO year={year}: cross=£{cross_cost:,.2f} "
                f"vs src=£{float(ro_lookup[year]):,.2f}"
            )
