"""Cross-scheme aggregation — long-format join over shipped scheme annual_summary parquets.

Plan 06-01. Phase 6 portal scheme module's only derivation. Reads each per-scheme
``annual_summary.parquet`` and emits ``cross_scheme.parquet`` in the long format
documented in ``schemas/portal.py::CrossSchemeRow``.

Determinism contract (D-21):
- Pure function of upstream parquet content.
- Final sort is ``(year ASC, scheme ASC)`` with ``kind="mergesort"`` for stability.
- No clock reads, no randomness.
- Uses the shared deterministic Parquet writer from
  ``schemes/cfd/cost_model._write_parquet`` (D-22) — import, do NOT re-implement.

Sources consumed:
- ``data/derived/cfd/annual_summary.parquet``
- ``data/derived/ro/annual_summary.parquet`` (filter ``country == 'GB'``;
  drop ``ro_cost_gbp`` NaN rows)

CRITICAL HAZARDS (per PATTERNS.md §"cross_scheme_model.py" Critical hazards):
1. RO ``country == 'GB'`` filter is MANDATORY — else NI rows double-count as a
   separate scheme.
2. RO ``ro_cost_gbp`` is NaN for SY1-SY4 + 2024 → drop NaN-cost rows.
3. CfD 2026 partial year is still emitted (X1 All-time band); the
   ``latest_fully_reconciled_year()`` helper excludes partial years.
4. RO year=2018 is absent (SY17 deferred) — gap is documented; do NOT interpolate.
5. Don't carry RO-internal sensitivity columns (e-ROC alternative cost or
   mutualisation-delta) into the cross-scheme grain — those belong in
   ``schemes/ro/`` only.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from uk_subsidy_tracker import PROJECT_ROOT
from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.data.uk_households import UK_HOUSEHOLDS
from uk_subsidy_tracker.schemas.portal import CrossSchemeRow, emit_schema_json

# Shared deterministic Parquet writer (D-22). Import, do NOT re-implement.
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet


def _read_cfd_long() -> pd.DataFrame:
    """Project CfD ``annual_summary.parquet`` into the cross-scheme long format."""
    src = PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    return pd.DataFrame({
        "year": df["year"],
        "scheme": "CfD",
        "cost_gbp": df["cfd_payments_gbp"],
        "premium_gbp": df["premium_over_gas_gbp"],
        "generation_mwh": df["cfd_generation_mwh"],
        "methodology_version": df["methodology_version"],
    })


def _read_ro_long() -> pd.DataFrame:
    """Project RO ``annual_summary.parquet`` into the cross-scheme long format.

    HAZARD #1 + #2 mitigation: filter ``country == 'GB'`` to drop NI rows
    (would otherwise double-count as a separate scheme), AND drop ``ro_cost_gbp``
    NaN rows (SY1-SY4 pre-EU-ETS RO years + 2024 price-data-gated).
    """
    src = PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    # D-12 / HAZARD #1+#2: GB-only headline scope; drop NI + NaN-cost rows.
    df = df[(df["country"] == "GB") & df["ro_cost_gbp"].notna()]
    return pd.DataFrame({
        "year": df["year"],
        "scheme": "RO",
        "cost_gbp": df["ro_cost_gbp"],
        "premium_gbp": df["premium_gbp"],
        "generation_mwh": df["ro_generation_mwh"],
        "methodology_version": df["methodology_version"],
    })


def build_cross_scheme(output_dir: Path) -> pd.DataFrame:
    """Emit ``cross_scheme.parquet`` + ``cross_scheme.schema.json`` under ``output_dir``.

    Pure function of upstream per-scheme parquet content. Phases 7-12 append
    one ``_read_<scheme>_long()`` projector per scheme to the ``parts`` list.

    Returns the in-memory DataFrame that was written to Parquet, useful for
    test fixtures that want to assert on the join result without re-reading
    from disk.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    parts = [_read_cfd_long(), _read_ro_long()]  # Phases 7-12 append here.
    parts = [p for p in parts if not p.empty]

    columns = list(CrossSchemeRow.model_fields.keys())

    if not parts:
        # Empty-but-typed frame so column order still matches D-10.
        long = pd.DataFrame(columns=columns)
        long = long.astype({
            "year": "int64",
            "scheme": "object",
            "cost_gbp": "float64",
            "premium_gbp": "float64",
            "generation_mwh": "float64",
            "households_uk": "int64",
            "methodology_version": "object",
        })
        _write_parquet(long, output_dir / "cross_scheme.parquet")
        emit_schema_json(CrossSchemeRow, output_dir / "cross_scheme.schema.json")
        return long

    long = pd.concat(parts, ignore_index=True)

    # Per-year UK households join. Use nullable Int64 to handle pre-2014 RO years
    # where the dict has no key (HAZARD: pre-2014 households absent — see RESEARCH Q3).
    long["households_uk"] = long["year"].map(UK_HOUSEHOLDS).astype("Int64")

    # D-12 carry-through — methodology_version pinned to the live constant.
    long["methodology_version"] = METHODOLOGY_VERSION

    # D-10 column order = CrossSchemeRow field declaration order.
    long = long[columns]

    # D-21 deterministic sort: (year ASC, scheme ASC) with stable mergesort.
    long = long.sort_values(["year", "scheme"], kind="mergesort").reset_index(drop=True)

    _write_parquet(long, output_dir / "cross_scheme.parquet")
    emit_schema_json(CrossSchemeRow, output_dir / "cross_scheme.schema.json")
    return long
