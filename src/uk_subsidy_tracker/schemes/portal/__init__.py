"""Portal scheme module — ARCHITECTURE §6.1 contract (Plan 06-01).

Five module-level callables satisfying the ``SchemeModule`` Protocol declared in
``uk_subsidy_tracker.schemes.__init__``. The portal is downstream of all per-scheme
refreshes — it reads each shipped scheme's ``annual_summary.parquet`` and emits
``cross_scheme.parquet``.

Public surface (ARCHITECTURE §6.1):
- ``DERIVED_DIR``: where the cross-scheme Parquet lives (``data/derived/portal/``).
- ``upstream_changed()``: mtime-based dirty-check vs shipped scheme parquets.
- ``refresh()``: no-op (no upstream URL — the portal is a downstream aggregator).
- ``rebuild_derived(output_dir)``: long-format join → ``cross_scheme.parquet``.
- ``regenerate_charts()``: delegate to ``uk_subsidy_tracker.plotting.__main__``.
- ``validate()``: presence + methodology + per-scheme cost reconciliation.

Helper:
- ``latest_fully_reconciled_year()``: max year where both CfD and RO have
  validated ``annual_summary.parquet`` rows. Today (2026-04-25) = 2023.

Protocol conformance is validated at runtime::

    >>> from uk_subsidy_tracker.schemes import portal, SchemeModule
    >>> isinstance(portal, SchemeModule)
    True
"""
from __future__ import annotations

from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes.portal._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)

DERIVED_DIR: Path = PROJECT_ROOT / "data" / "derived" / "portal"

# Stable registration order — appended to as Phases 7-12 ship new schemes.
# Alphabetical for grep-discoverability; UI-SPEC §"Stack order on X1" reorders
# at render time per visual band-stacking rules.
SHIPPED_SCHEMES: tuple[str, ...] = ("CfD", "RO")

# Latest CfD calendar year fully reconciled (no partial-year settlements).
# Per RESEARCH §"Open Questions Q2": 2025 is the most recent complete CfD CY;
# 2026 is partial (in-progress). Used by latest_fully_reconciled_year().
LATEST_COMPLETE_CFD_YEAR: int = 2025


def upstream_changed() -> bool:
    """Return True iff cross_scheme.parquet is absent OR any source mtime is newer."""
    return _upstream_changed()


def refresh() -> None:
    """No-op — the portal has no upstream URL to fetch."""
    _refresh()


def rebuild_derived(output_dir: Path | None = None) -> None:
    """Emit ``cross_scheme.parquet`` + ``cross_scheme.schema.json`` under ``output_dir``.

    Pure function of upstream per-scheme parquet content (D-21). If ``output_dir``
    is None, writes to ``DERIVED_DIR = data/derived/portal/``. Otherwise writes
    to the caller-supplied path (test fixtures depend on this).
    """
    target = output_dir if output_dir is not None else DERIVED_DIR
    target.mkdir(parents=True, exist_ok=True)
    from uk_subsidy_tracker.schemes.portal.cross_scheme_model import (
        build_cross_scheme,
    )
    build_cross_scheme(target)


def regenerate_charts() -> None:
    """Delegate to the existing plotting entry point (D-02 — charts untouched).

    Phase 6 chart files (X1-X5) land in Wave 2/3 of this phase; until then this
    function runs the existing plotting pipeline unchanged. Exists to satisfy
    the ``SchemeModule`` contract.
    """
    import runpy

    runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")


def validate() -> list[str]:
    """Return a list of human-readable warnings (empty list = all clean).

    Three checks per RESEARCH §"`__init__.py` skeleton" lines 355-399:

    1. Presence — every shipped scheme has at least one row in
       ``cross_scheme.parquet``.
    2. ``methodology_version`` matches the live ``counterfactual.METHODOLOGY_VERSION``
       constant (D-12 chain).
    3. Per-scheme cost reconciliation against the source ``annual_summary.parquet``
       (RO needs ``country == 'GB'`` filter to match the cross-scheme join site).

    All checks short-circuit cleanly on a missing Parquet so a partial pipeline
    state never trip-wires this function.
    """
    import pyarrow.parquet as pq

    warnings: list[str] = []

    cross = DERIVED_DIR / "cross_scheme.parquet"
    if not cross.exists():
        return [f"validate: {cross} missing — run rebuild_derived()"]
    df = pq.read_table(cross).to_pandas()

    # Check 1: every shipped scheme has at least one row.
    schemes_present = set(df["scheme"].unique().tolist())
    missing = set(SHIPPED_SCHEMES) - schemes_present
    if missing:
        warnings.append(
            f"validate: missing scheme rows: {sorted(missing)}"
        )

    # Check 2: methodology_version matches the live constant (D-12 chain).
    versions = set(df["methodology_version"].dropna().unique().tolist())
    if versions and versions != {METHODOLOGY_VERSION}:
        warnings.append(
            f"validate: methodology_version drift — column has {versions!r}, "
            f"constant is {METHODOLOGY_VERSION!r}"
        )

    # Check 3: per-scheme cost reconciliation against source annual_summary.
    from uk_subsidy_tracker.schemes import cfd as cfd_mod
    from uk_subsidy_tracker.schemes import ro as ro_mod
    sources = {
        "CfD": (cfd_mod.DERIVED_DIR / "annual_summary.parquet", "cfd_payments_gbp"),
        "RO": (ro_mod.DERIVED_DIR / "annual_summary.parquet", "ro_cost_gbp"),
    }
    for scheme_code, (src, cost_col) in sources.items():
        if not src.exists():
            continue
        src_df = pq.read_table(src).to_pandas()
        if scheme_code == "RO":
            src_df = src_df[src_df["country"] == "GB"]
        src_total = float(src_df[cost_col].dropna().sum())
        cross_total = float(df[df["scheme"] == scheme_code]["cost_gbp"].sum())
        if src_total > 0 and abs(cross_total - src_total) / src_total > 0.001:
            warnings.append(
                f"validate: {scheme_code} cost drift — cross_scheme £{cross_total:,.0f} "
                f"vs annual_summary £{src_total:,.0f} (>0.1%)"
            )

    return warnings


def latest_fully_reconciled_year() -> int:
    """Most recent year for which BOTH CfD and RO have validated parquet rows.

    Per RESEARCH §"latest_fully_reconciled_year rule" lines 663-693. Used by
    Wave 5 docs/index.md headline-card values + Wave 6 headline-sync test.

    Today's value (2026-04-25): 2023 — intersection of:
    - CfD complete CYs ({2016-2025}, capped by ``LATEST_COMPLETE_CFD_YEAR=2025``)
    - RO complete years (GB-only with non-null ``ro_cost_gbp``):
      ``{2006-2017, 2019-2023}`` (note: 2018 SY17 gap; 2024 cost=NaN)
    - Intersection: ``{2016, 2017, 2019, 2020, 2021, 2022, 2023}`` → max = 2023

    Raises RuntimeError if the intersection is empty (data tree corrupted or
    bootstrap state).
    """
    import pyarrow.parquet as pq

    cfd_path = PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet"
    ro_path = PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet"

    if not cfd_path.exists() or not ro_path.exists():
        raise RuntimeError(
            "latest_fully_reconciled_year: per-scheme annual_summary.parquet missing — "
            "run cfd.rebuild_derived() and ro.rebuild_derived() first"
        )

    cfd_df = pq.read_table(cfd_path).to_pandas()
    ro_df = pq.read_table(ro_path).to_pandas()

    # CfD: a year is "complete" when year <= LATEST_COMPLETE_CFD_YEAR.
    cfd_complete = {
        int(y) for y in cfd_df["year"].unique()
        if int(y) <= LATEST_COMPLETE_CFD_YEAR
    }

    # RO: a year is "complete" when GB row has non-null ro_cost_gbp.
    ro_gb = ro_df[ro_df["country"] == "GB"]
    ro_complete = {
        int(y) for y in ro_gb.dropna(subset=["ro_cost_gbp"])["year"].unique()
    }

    intersection = cfd_complete & ro_complete
    if not intersection:
        raise RuntimeError(
            "latest_fully_reconciled_year: empty intersection — "
            f"CfD complete years {sorted(cfd_complete)!r} ∩ "
            f"RO complete years {sorted(ro_complete)!r} = ∅"
        )
    return max(intersection)


__all__ = [
    "DERIVED_DIR",
    "LATEST_COMPLETE_CFD_YEAR",
    "SHIPPED_SCHEMES",
    "latest_fully_reconciled_year",
    "rebuild_derived",
    "refresh",
    "regenerate_charts",
    "upstream_changed",
    "validate",
]
