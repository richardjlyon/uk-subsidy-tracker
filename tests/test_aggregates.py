"""Row-conservation invariants on the CfD pipeline (TEST-03 scaffolding).

Phase 2 pre-Parquet scaffolding. Invariant: aggregating CFD_Payments_GBP
by year must equal aggregating by (year, Technology) and then collapsing
back to year. A mismatch means the groupby dropped rows — typically a
NaN in the `Technology` column.

Formal TEST-03 is satisfied in Phase 4 when Parquet-aggregate assertions
are added to this same file.
"""

import pandas as pd
import pytest

from uk_subsidy_tracker.data import load_lccc_dataset


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
