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

from pathlib import Path

import pytest
import yaml

from tests.fixtures import BenchmarkEntry, load_benchmarks
from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.data import load_lccc_dataset

# --- Divergences YAML loader (per-year xfail map for REF reconciliation) --- #

_DIVERGENCES_YAML = Path(__file__).parent / "fixtures" / "divergences.yaml"
_DIVERGENCE_DOC = (
    PROJECT_ROOT / ".planning" / "phases" / "05-ro-module" / "05-09-DIVERGENCE.md"
)


def _load_xfail_years() -> dict[int, str]:
    """Load per-year xfail map from tests/fixtures/divergences.yaml.

    Returns a dict mapping calendar year -> xfail reason string.
    Called at collection time; raises if the file is missing (fail loud —
    no try/except shim: if divergences.yaml is absent, tests must fail).

    The file must exist. It is part of the test fixture tree, not optional.
    """
    raw = yaml.safe_load(_DIVERGENCES_YAML.read_text())
    return {
        entry["year"]: entry["reason"]
        for entry in raw.get("xfailed_years", [])
    }


# Build xfail map at collection time (module-level, no try/except by design).
_XFAIL_YEARS: dict[int, str] = _load_xfail_years()

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

REF_TOLERANCE_PCT: float = 3.0
"""REF Constable 2025 primary RO benchmark tolerance (Phase 5 D-14 HARD BLOCK).

Per CONTEXT D-14 (Phase 5 RO-06, ROADMAP SC #3): if divergence exceeds 3%,
investigate root cause BEFORE raising tolerance. Investigate in this order:

  1. REF scope difference — is REF excluding NIRO? including mutualisation?
     SY vs CY skew? Document scope-delta in benchmarks.yaml audit header.
  2. Banding error — R1 regression in ro_bandings.yaml or ofgem_ro.load_*
     cross-check on station_month.rocs_computed vs rocs_issued.
  3. Carbon-price extension regression — D-05 2005-2017 values wrong?
     Check DEFAULT_CARBON_PRICES pre-2018 entries.

Only raise tolerance with a CHANGES.md `## Methodology versions` entry (D-07).
Unlike the D-11-fallback external anchors, REF reconciliation is binary
(hard block) — no silent `pytest.skip` when ref_constable is empty."""

_TOLERANCE_BY_SOURCE: dict[str, float] = {
    "ofgem_transparency": OFGEM_TOLERANCE_PCT,
    "obr_efo": OBR_EFO_TOLERANCE_PCT,
    "desnz_energy_trends": DESNZ_TOLERANCE_PCT,
    "hoc_library": HOC_LIBRARY_TOLERANCE_PCT,
    "nao_audit": NAO_TOLERANCE_PCT,
    "ref_constable": REF_TOLERANCE_PCT,  # Phase 5 Plan 05-09 (D-13 / D-14)
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


# --- REF Constable RO reconciliation (CONTEXT D-13 / D-14 — HARD BLOCK) --- #


@pytest.fixture(scope="module")
def ro_annual_totals_gbp_bn() -> dict[int, float]:
    """Pipeline yearly RO totals in £bn (GB-only per D-12), keyed by calendar year.

    Phase 05.2: reads annual_summary.parquet (aggregate grain — D-04 + D-05).
    The dormant station-level grain is absent from the tree while DORMANT_STATION_LEVEL
    is True; aggregate grain is the sole source of RO cost data.

    Sums ``ro_cost_gbp`` from ``data/derived/ro/annual_summary.parquet``
    filtered to ``country == 'GB'``, grouped by ``year`` (calendar year —
    D-07 primary plotting axis). Requires ro.rebuild_derived() to have run;
    invoke via ``uk_subsidy_tracker.schemes.ro.rebuild_derived()``.

    Empty-Parquet / missing-file handling: returns ``{}`` so the parametrised
    test body can route through the D-14 diagnostic path. The sentinel file
    escape hatch (DIVERGENCE.md) keeps all 22 REF parametrisations xfailed
    until Plan 06 deletes the sentinel.
    """
    import pyarrow.parquet as pq
    from uk_subsidy_tracker.schemes import ro

    path = ro.DERIVED_DIR / "annual_summary.parquet"
    if not path.exists():
        return {}
    df = pq.read_table(path).to_pandas()
    if len(df) == 0:
        return {}
    gb = df[df["country"] == "GB"].copy()
    if len(gb) == 0:
        return {}
    totals_gbp = gb.groupby("year")["ro_cost_gbp"].sum()
    return (totals_gbp / 1e9).astype(float).to_dict()


def _ref_entries() -> list[BenchmarkEntry]:
    """Load REF Constable entries; fail loud if empty (D-14 no-skip policy).

    Called at pytest collection time for the parametrisation below. If
    ``benchmarks.yaml::ref_constable`` is unexpectedly empty, return an
    empty list (the collection produces zero parameter cases); a
    companion collection-time assertion would mask the ``load_benchmarks``
    failure mode we actually care about (Pydantic validation error).
    """
    try:
        entries = load_benchmarks().ref_constable
    except Exception:  # noqa: BLE001 — collection-time robustness
        return []
    return entries


def _parametrised_ref_entries() -> list:
    """Build parametrised entries with per-year xfail marks from divergences.yaml.

    Years listed in _XFAIL_YEARS receive pytest.mark.xfail(strict=False,
    reason=<entry reason>). All other years run as hard assertions (D-14).

    The xfail map is loaded from tests/fixtures/divergences.yaml at module
    import time (no try/except — file absence is a hard failure, not silent).
    """
    params = []
    for entry in _ref_entries():
        reason = _XFAIL_YEARS.get(entry.year)
        if reason is not None:
            params.append(
                pytest.param(
                    entry,
                    marks=pytest.mark.xfail(strict=False, reason=reason),
                )
            )
        else:
            params.append(entry)
    return params


# Dead code — kept for historical traceability (Phase 5 Plan 05-09 sentinel
# mechanism). The blanket sentinel xfail was replaced in Phase 05.2 Plan 06
# by per-year xfail entries in tests/fixtures/divergences.yaml. The file
# now exists as a per-year record (not a blanket sentinel), so this check
# always evaluates to True but the xfail is applied at parametrisation time
# above, not here. Do not remove this reference — it documents the transition.
_DIVERGENCE_SENTINEL = (
    PROJECT_ROOT / ".planning" / "phases" / "05-ro-module" / "05-09-DIVERGENCE.md"
)


@pytest.mark.parametrize(
    "entry",
    _parametrised_ref_entries(),
    ids=lambda e: f"ref_constable-{e.year}" if isinstance(e, BenchmarkEntry) else f"ref_constable-{e.values[0].year}",
)
def test_ref_constable_ro_reconciliation(
    entry: BenchmarkEntry, ro_annual_totals_gbp_bn: dict[int, float]
) -> None:
    """RO-06 / D-14 / ROADMAP SC #3: pipeline ro_cost_gbp aggregate within ±3%
    of REF Constable 2025 Table 1 per-year figure.

    HARD BLOCK: if this fails for a non-xfailed year, investigate BEFORE
    raising the tolerance.

    Per-year xfail escape hatch (Phase 05.2 Plan 06):
      Years listed in tests/fixtures/divergences.yaml are xfailed with
      per-entry root-cause reasons. See .planning/phases/05-ro-module/
      05-09-DIVERGENCE.md for the methodology record and unlock conditions.
      Do NOT widen REF_TOLERANCE_PCT — the only sanctioned path is to fix
      the pipeline and remove the entry from divergences.yaml.
    """
    ours = ro_annual_totals_gbp_bn.get(entry.year)
    if ours is None:
        pytest.fail(
            f"Pipeline has no data for year {entry.year} — either the RO "
            f"derived Parquet was not built before this test or "
            f"annual_summary.parquet filtering to country='GB' dropped the "
            f"year. Rebuild via `uv run python -c \"from uk_subsidy_tracker"
            f".schemes import ro; ro.rebuild_derived()\"`, then re-run. "
            f"Phase 05.2: reads annual_summary.parquet (aggregate grain, D-05). "
            f"Unlock path: see {_DIVERGENCE_SENTINEL.name} per-year table."
        )

    divergence_pct = abs(ours - entry.value_gbp_bn) / entry.value_gbp_bn * 100.0
    assert divergence_pct <= REF_TOLERANCE_PCT, (
        f"REF Constable reconciliation FAILED for {entry.year} (D-14 HARD BLOCK):\n"
        f"  pipeline:    £{ours:.4f} bn\n"
        f"  REF Table 1: £{entry.value_gbp_bn:.4f} bn\n"
        f"  divergence:  {divergence_pct:.2f}% (> {REF_TOLERANCE_PCT}% tolerance)\n"
        f"\nInvestigate before adjusting tolerance (per D-14):\n"
        f"  1. REF scope — is it excluding NIRO? including mutualisation? SY vs CY?\n"
        f"     (Check benchmarks.yaml audit header vs our D-12 scope.)\n"
        f"  2. Banding error — cross-check station_month rocs_computed vs rocs_issued.\n"
        f"  3. Carbon-price extension — is DEFAULT_CARBON_PRICES[{entry.year}] sensible?\n"
        f"URL: {entry.url}"
    )


# --- Divergences YAML sync check --- #


def test_divergences_yaml_sync() -> None:
    """Structural sync-check: divergences.yaml and DIVERGENCE.md stay in sync.

    Verifies:
    1. divergences.yaml is loadable and has valid structure.
    2. Every year in divergences.yaml appears in benchmarks.yaml::ref_constable
       (no phantom entries referencing non-existent REF years).
    3. The set of xfailed years from divergences.yaml is internally consistent
       (no duplicate year entries).
    4. DIVERGENCE.md exists (the human-readable record must not be deleted
       while divergences.yaml still has entries).

    This test does NOT parse DIVERGENCE.md tables — it trusts that the
    human maintaining the file keeps them aligned. The machine-readable
    source of truth is divergences.yaml.
    """
    # 1. divergences.yaml is loadable
    assert _DIVERGENCES_YAML.exists(), (
        f"tests/fixtures/divergences.yaml is missing. "
        f"It is the machine-readable xfail map for REF reconciliation. "
        f"Do not delete it while there are active per-year xfail entries."
    )
    raw = yaml.safe_load(_DIVERGENCES_YAML.read_text())
    assert isinstance(raw, dict), "divergences.yaml must parse to a dict"
    entries = raw.get("xfailed_years", [])
    assert isinstance(entries, list), "divergences.yaml::xfailed_years must be a list"

    # 2. No phantom years (every xfailed year must be in benchmarks.yaml)
    ref_years = {e.year for e in load_benchmarks().ref_constable}
    xfail_years_in_yaml = [e["year"] for e in entries]
    for year in xfail_years_in_yaml:
        assert year in ref_years, (
            f"divergences.yaml entry year={year} does not appear in "
            f"benchmarks.yaml::ref_constable. Either the year is wrong or "
            f"it was removed from benchmarks.yaml without cleaning up divergences.yaml."
        )

    # 3. No duplicates
    assert len(xfail_years_in_yaml) == len(set(xfail_years_in_yaml)), (
        f"divergences.yaml has duplicate year entries: "
        f"{[y for y in xfail_years_in_yaml if xfail_years_in_yaml.count(y) > 1]}"
    )

    # 4. DIVERGENCE.md exists while there are active xfail entries
    if entries:
        assert _DIVERGENCE_DOC.exists(), (
            f"{_DIVERGENCE_DOC.name} must exist while divergences.yaml has "
            f"active xfail entries. The human-readable record cannot be deleted "
            f"before all per-year entries are resolved and removed from divergences.yaml."
        )
