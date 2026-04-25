"""RO scheme module — ARCHITECTURE §6.1 contract.

Five module-level callables satisfying the ``SchemeModule`` Protocol declared
in ``uk_subsidy_tracker.schemes.__init__``. Mirrors ``schemes/cfd/`` verbatim
with RO-specific logic substitutions.

Public surface (ARCHITECTURE §6.1):
- ``DERIVED_DIR``: where this scheme's Parquet lives (``data/derived/ro/``).
- ``upstream_changed()``: SHA-compare against Ofgem raw sidecars (Plan 05-01).
- ``refresh()``: re-fetch Ofgem raw files (XLSX only when dormant; full when active).
- ``rebuild_derived(output_dir)``: raw → Parquet grains (aggregate grain while dormant).
- ``regenerate_charts()``: delegate to ``uk_subsidy_tracker.plotting.__main__``.
- ``validate()``: four D-04 post-rebuild sanity checks; empty list = clean.

Protocol conformance is validated at runtime::

    >>> from uk_subsidy_tracker.schemes import ro, SchemeModule
    >>> isinstance(ro, SchemeModule)
    True
"""
from __future__ import annotations

from pathlib import Path

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.schemes.ro._refresh import (
    refresh as _refresh,
    upstream_changed as _upstream_changed,
)

DERIVED_DIR: Path = PROJECT_ROOT / "data" / "derived" / "ro"

# Module-level dormancy flag (D-07 — single switch to flip on backlog 999.1).
# Grep-discoverable: `grep -rn "DORMANT_STATION_LEVEL" src/`
DORMANT_STATION_LEVEL: bool = True


def upstream_changed() -> bool:
    """Return True iff any Ofgem raw file's sha256 differs from its sidecar."""
    return _upstream_changed()


def refresh() -> None:
    """Re-fetch Ofgem raw files (delegates to ``_refresh.refresh``)."""
    _refresh()


def rebuild_derived(output_dir: Path | None = None) -> None:
    """Emit RO derived Parquet grains under the target directory.

    Phase 05.2 + D-05 + D-07: when DORMANT_STATION_LEVEL is True, emits
    only annual_summary.parquet + by_technology.parquet from aggregate
    sources. Station-level grains (station_month, by_allocation_round,
    forward_projection) are skipped — no file written; manifest.json
    correspondingly omits them.

    Pure function of ``data/raw/ofgem/`` content (D-21). If ``output_dir`` is
    None, writes to ``DERIVED_DIR = data/derived/ro/``. Otherwise writes to
    the caller-supplied path (test fixtures depend on this).
    """
    target = output_dir if output_dir is not None else DERIVED_DIR
    target.mkdir(parents=True, exist_ok=True)

    if DORMANT_STATION_LEVEL:
        from uk_subsidy_tracker.schemes.ro.aggregate_model import (
            build_annual_summary_aggregate,
            build_by_technology_aggregate,
        )
        build_annual_summary_aggregate(target)
        build_by_technology_aggregate(target)
        return

    # Station-level path (re-activated on backlog 999.1)
    from uk_subsidy_tracker.schemes.ro.aggregation import (
        build_annual_summary,
        build_by_allocation_round,
        build_by_technology,
    )
    from uk_subsidy_tracker.schemes.ro.cost_model import build_station_month
    from uk_subsidy_tracker.schemes.ro.forward_projection import build_forward_projection

    build_station_month(target)
    build_annual_summary(target)
    build_by_technology(target)
    build_by_allocation_round(target)
    build_forward_projection(target)


def regenerate_charts() -> None:
    """Delegate to the existing plotting entry point (D-02 — charts untouched).

    RO-specific chart files land in Plan 05-08; until then this function
    runs the existing plotting pipeline unchanged. Exists to satisfy the
    ``SchemeModule`` contract.
    """
    import runpy

    runpy.run_module("uk_subsidy_tracker.plotting", run_name="__main__")


def validate() -> list[str]:
    """Return a list of human-readable warnings (empty list = all clean).

    Four D-04 post-rebuild sanity checks:

    1. Banding divergence — per-station Ofgem-published vs YAML-computed ROCs
       delta; warns if >10 stations or >5% of station population exceed 1%.
       (Skipped when DORMANT_STATION_LEVEL=True; station_month.parquet absent.)
    2. REF Constable drift — 2011-2022 ``ro_cost_gbp`` aggregate vs the
       ``ref_constable`` benchmark fixture; warns at >3% drift (the hard-block
       version lives in ``tests/test_benchmarks.py``; this is the cheap
       post-rebuild warner).
    3. ``methodology_version`` column consistency across all available RO Parquets.
    4. ``forward_projection`` sanity — negative costs or >50% year-on-year
       ``remaining_committed_mwh`` jumps within a technology.
       (Skipped when DORMANT_STATION_LEVEL=True; forward_projection.parquet absent.)

    All checks short-circuit cleanly on missing Parquets or empty data so a
    partial rebuild never trip-wires this function.
    """
    import pyarrow.parquet as pq

    warnings: list[str] = []

    # ---- Check 1 — banding divergence (D-04 Check 1) ----
    # Only meaningful when station_month.parquet exists (station-level path).
    sm_path = DERIVED_DIR / "station_month.parquet"
    if sm_path.exists():
        import pandas as pd  # noqa: F401
        sm = pq.read_table(sm_path).to_pandas()
        if (
            len(sm) > 0
            and "rocs_issued" in sm.columns
            and "rocs_computed" in sm.columns
        ):
            nonzero_issued = sm[sm["rocs_issued"] > 0].copy()
            if len(nonzero_issued) > 0:
                nonzero_issued["delta_pct"] = (
                    (nonzero_issued["rocs_issued"] - nonzero_issued["rocs_computed"]).abs()
                    / nonzero_issued["rocs_issued"]
                )
                divergent = nonzero_issued[nonzero_issued["delta_pct"] > 0.01]
                station_count = nonzero_issued["station_id"].nunique()
                divergent_stations = divergent["station_id"].nunique() if len(divergent) else 0
                if divergent_stations > 10 or (
                    station_count > 0 and divergent_stations / station_count > 0.05
                ):
                    warnings.append(
                        f"D-04 Check 1 (banding divergence): {divergent_stations} stations "
                        f"have >1% Ofgem-vs-YAML rocs delta (threshold: >10 or >5% of {station_count})"
                    )

    # ---- Check 2 — REF benchmark drift (D-04 Check 2) ----
    # Cheap post-rebuild drift warner. Hard-block reconciliation lives in
    # tests/test_benchmarks.py (Plan 05-09). Complementary layers.
    annual_path = DERIVED_DIR / "annual_summary.parquet"
    if annual_path.exists():
        ann = pq.read_table(annual_path).to_pandas()
        if "ro_cost_gbp" in ann.columns and len(ann) > 0:
            # Cheap negative-sanity short-circuit (skip NaN rows from SY1-SY4).
            cost_col = ann["ro_cost_gbp"].dropna()
            if len(cost_col) > 0 and (cost_col < 0).any():
                warnings.append(
                    "D-04 Check 2: negative ro_cost_gbp in annual_summary"
                )

            # REF drift aggregate check (best-effort; silent if fixture absent).
            try:
                import yaml  # pyyaml is already a project dep

                ref_path = (
                    PROJECT_ROOT / "tests" / "fixtures" / "benchmarks.yaml"
                )
                if ref_path.exists() and "year" in ann.columns:
                    raw = yaml.safe_load(ref_path.read_text())
                    ref_block = (raw or {}).get("ref_constable", {})
                    ref_annual = ref_block.get("annual_gbp") or {}
                    if ref_annual:
                        window = ann[(ann["year"] >= 2011) & (ann["year"] <= 2022)]
                        built = float(window["ro_cost_gbp"].sum())
                        ref_total = float(
                            sum(
                                float(v)
                                for k, v in ref_annual.items()
                                if 2011 <= int(k) <= 2022
                            )
                        )
                        if ref_total > 0:
                            drift_pct = abs(built - ref_total) / ref_total * 100.0
                            if drift_pct > 3.0:
                                warnings.append(
                                    f"D-04 Check 2 (REF drift): RO 2011-2022 built aggregate "
                                    f"£{built:,.0f} vs ref_constable £{ref_total:,.0f} "
                                    f"(drift {drift_pct:.2f}% > 3.0% tolerance)"
                                )
            except (FileNotFoundError, KeyError, yaml.YAMLError):
                pass

    # ---- Check 3 — methodology_version consistency (D-04 Check 3) ----
    for grain in [
        "station_month",
        "annual_summary",
        "by_technology",
        "by_allocation_round",
        "forward_projection",
    ]:
        path = DERIVED_DIR / f"{grain}.parquet"
        if path.exists():
            df = pq.read_table(path).to_pandas()
            if "methodology_version" in df.columns and len(df) > 0:
                unique = set(df["methodology_version"].dropna().unique())
                if unique and unique != {METHODOLOGY_VERSION}:
                    warnings.append(
                        f"D-04 Check 3: {grain}.parquet methodology_version drift — "
                        f"expected {{{METHODOLOGY_VERSION!r}}}, got {unique}"
                    )

    # ---- Check 4 — forward-projection sanity (D-04 Check 4) ----
    fp_path = DERIVED_DIR / "forward_projection.parquet"
    if fp_path.exists():
        fp = pq.read_table(fp_path).to_pandas()
        if len(fp) > 0 and "remaining_cost_gbp" in fp.columns:
            if (fp["remaining_cost_gbp"] < 0).any():
                warnings.append(
                    "D-04 Check 4: negative remaining_cost_gbp in forward_projection"
                )
            if (
                "remaining_committed_mwh" in fp.columns
                and "year" in fp.columns
                and "technology" in fp.columns
            ):
                import numpy as np

                for tech, sub in fp.sort_values("year").groupby(
                    "technology", observed=True
                ):
                    mwh = sub["remaining_committed_mwh"].to_numpy()
                    if len(mwh) >= 2:
                        with np.errstate(divide="ignore", invalid="ignore"):
                            jumps = np.abs(np.diff(mwh)) / np.where(
                                mwh[:-1] > 0, mwh[:-1], 1
                            )
                        if (jumps > 0.5).any():
                            warnings.append(
                                f"D-04 Check 4: forward_projection remaining_committed_mwh "
                                f"jumps >50% across adjacent years for technology={tech!r}"
                            )

    return warnings


__all__ = [
    "DERIVED_DIR",
    "DORMANT_STATION_LEVEL",
    "upstream_changed",
    "refresh",
    "rebuild_derived",
    "regenerate_charts",
    "validate",
]
