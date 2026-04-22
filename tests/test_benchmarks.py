"""Reconcile our CfD pipeline yearly totals against published benchmarks (TEST-04).

Two check types:

1. **LCCC self-reconciliation floor** (MANDATORY, 0.1% tolerance, CONTEXT D-10).
   Our pipeline reads LCCC raw data. If our aggregation diverges from LCCC's
   own published aggregate by > 0.1%, that is a PIPELINE BUG, not a
   methodology divergence. This check is always-included, always-green,
   never parameterised away.

2. **External anchors** — OBR, Ofgem, DESNZ, HoC Library, NAO. Looser
   tolerances (3–5%) reflect legitimate basis differences (FY-vs-CY,
   CPI indexing, scheme-subset scope, retrieval-year drift). Tolerance
   bumps require a CHANGES.md entry under `## Methodology versions`
   per CONTEXT D-07. Zero external entries is allowed per D-11 fallback.
"""

import pytest

from tests.fixtures import BenchmarkEntry, load_benchmarks
from uk_subsidy_tracker.data import load_lccc_dataset

# --- Tolerance constants (CONTEXT D-06 — docstring rationale mandatory) --- #

LCCC_SELF_TOLERANCE_PCT = 0.1
"""Red line per CONTEXT D-10. Our pipeline reads LCCC raw data; a divergence
here means our groupby / date parsing / unit conversion is off. This is a
pipeline bug, not a methodology divergence."""

OBR_EFO_TOLERANCE_PCT = 5.0
"""OBR reports financial-year (April–March) CfD spend; we report calendar-year.
Quarterly-roll-over skew + carbon-price CPI basis differences justify the
looser tolerance. Bumping this requires a CHANGES.md `## Methodology
versions` entry per D-07."""

OFGEM_TOLERANCE_PCT = 5.0
"""Ofgem transparency dashboards may aggregate over a different scheme subset
(e.g. including-or-excluding supplier-levy adjustments). CHANGES.md entry
required to bump."""

DESNZ_TOLERANCE_PCT = 5.0
"""DESNZ Energy Trends uses a different retrieval snapshot; lag and revision
between their publication and ours drives a few-percent drift. CHANGES.md
entry required to bump."""

HOC_LIBRARY_TOLERANCE_PCT = 3.0
"""HoC Library briefings re-cite LCCC/DESNZ figures; drift should be small
(inherited basis). CHANGES.md entry required to bump."""

NAO_TOLERANCE_PCT = 3.0
"""NAO audits are point-in-time; figures should be close to our aggregate
for the same window. CHANGES.md entry required to bump."""

_TOLERANCE_BY_SOURCE: dict[str, float] = {
    "ofgem_transparency": OFGEM_TOLERANCE_PCT,
    "obr_efo": OBR_EFO_TOLERANCE_PCT,
    "desnz_energy_trends": DESNZ_TOLERANCE_PCT,
    "hoc_library": HOC_LIBRARY_TOLERANCE_PCT,
    "nao_audit": NAO_TOLERANCE_PCT,
}


# --- Fixtures --- #

@pytest.fixture(scope="module")
def annual_totals_gbp_bn() -> dict[int, float]:
    """Pipeline yearly CfD totals in £bn, keyed by calendar year."""
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df = df.copy()
    df["year"] = df["Settlement_Date"].dt.year
    totals_gbp = df.groupby("year")["CFD_Payments_GBP"].sum()
    return (totals_gbp / 1e9).to_dict()


@pytest.fixture(scope="module")
def benchmarks():
    return load_benchmarks()


# --- Mandatory LCCC floor (CONTEXT D-10) --- #

def test_lccc_self_reconciliation_floor(benchmarks, annual_totals_gbp_bn):
    """CONTEXT D-10: LCCC self-reconciliation must hold within 0.1%.

    A divergence here is a PIPELINE BUG (our groupby / dtype / unit handling
    is off), NOT a methodology divergence. Do not raise the tolerance to
    make this pass.
    """
    if not benchmarks.lccc_self:
        pytest.skip(
            "tests/fixtures/benchmarks.yaml has no `lccc_self:` entries — "
            "D-11 fallback is active. Populate with the calendar-year aggregate "
            "from the latest LCCC Annual Report & Accounts PDF to activate "
            "the mandatory floor check."
        )

    for entry in benchmarks.lccc_self:
        ours = annual_totals_gbp_bn.get(entry.year)
        assert ours is not None, (
            f"No pipeline data for year {entry.year} — benchmarks.yaml "
            f"references a year our LCCC CSV does not cover."
        )
        divergence_pct = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn * 100.0
        assert divergence_pct <= LCCC_SELF_TOLERANCE_PCT, (
            f"LCCC self-reconciliation failed for {entry.year}: "
            f"pipeline = £{ours:.4f} bn, LCCC published = £{entry.value_gbp_bn:.4f} bn, "
            f"divergence = {divergence_pct:.3f}% (> {LCCC_SELF_TOLERANCE_PCT}%). "
            f"Per CONTEXT D-10 this is a PIPELINE BUG. Fix the pipeline — "
            f"do NOT raise the tolerance. Source: {entry.url}."
        )


# --- Parametrised external-anchor checks (CONTEXT D-11 — may be empty) --- #

def _collect_external_entries() -> list[BenchmarkEntry]:
    """Collect external-anchor entries for parametrisation at collection time."""
    try:
        return load_benchmarks().all_external_entries()
    except Exception:  # noqa: BLE001
        return []


@pytest.mark.parametrize("entry", _collect_external_entries(), ids=lambda e: f"{e.source}-{e.year}")
def test_external_benchmark_within_tolerance(entry: BenchmarkEntry, annual_totals_gbp_bn):
    """External anchor within named tolerance per CONTEXT D-06.

    Failure options (D-07):
      (a) Fix the pipeline (most common when divergence is material);
      (b) Document a methodology-version-bumping divergence in CHANGES.md;
      (c) Raise the named tolerance constant with written rationale under
          `## Methodology versions`.
    Silent tolerance creep is explicitly forbidden.
    """
    ours = annual_totals_gbp_bn.get(entry.year)
    assert ours is not None, (
        f"No pipeline data for year {entry.year}; benchmarks.yaml entry "
        f"{entry.source}/{entry.year} cannot be checked."
    )
    tolerance = _TOLERANCE_BY_SOURCE.get(entry.source, entry.tolerance_pct)
    divergence_pct = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn * 100.0
    assert divergence_pct <= tolerance, (
        f"Benchmark divergence {entry.source}/{entry.year}: "
        f"pipeline = £{ours:.4f} bn, {entry.source} = £{entry.value_gbp_bn:.4f} bn, "
        f"divergence = {divergence_pct:.2f}% (> {tolerance}%). "
        f"Three options per D-06/D-07: (a) fix the pipeline, "
        f"(b) document a methodology-version-bumping divergence in CHANGES.md, "
        f"(c) raise the tolerance constant with written rationale in "
        f"CHANGES.md under `## Methodology versions`. "
        f"Source notes: {entry.notes}. URL: {entry.url}."
    )
