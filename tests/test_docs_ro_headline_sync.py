"""Regression guard: docs/schemes/ro.md headline number matches
data/derived/ro/annual_summary.parquet GB total (Phase 05.2 D-Claude's-Discretion).

The lead paragraph's "£NN.N bn" figure is the reconstructed GB headline;
this test enforces that prose tracks data to 1 decimal place. If the
aggregate pipeline emits a different figure on the next rebuild, this
test fails and forces either (a) a prose update or (b) a CHANGES.md
`## Methodology versions` audit entry per Phase 2 D-07.

TDD RED compromise (Phase 05.2 revision INFO #9): soft-skip when Parquet
missing, hard-assert when Parquet present. Plan 06 Task 3 re-runs this
test against real Parquet as the phase-exit hard gate.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
RO_MD = PROJECT_ROOT / "docs" / "schemes" / "ro.md"
ANNUAL_SUMMARY_PARQUET = PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet"

_HEADLINE_RE = re.compile(r"£\s*(\d+(?:\.\d+)?)\s*bn", re.IGNORECASE)


def _parquet_gb_total_gbp_bn() -> float:
    import pyarrow.parquet as pq
    df = pq.read_table(ANNUAL_SUMMARY_PARQUET).to_pandas()
    gb = df[df["country"] == "GB"]
    total_gbp = float(gb["ro_cost_gbp"].sum())
    return round(total_gbp / 1e9, 1)


def _prose_headline_gbp_bn() -> float | None:
    text = RO_MD.read_text(encoding="utf-8")
    # Look at the first ~30 lines after the H1 for the headline figure
    first_chunk = "\n".join(text.splitlines()[:40])
    m = _HEADLINE_RE.search(first_chunk)
    if m is None:
        return None
    return round(float(m.group(1)), 1)


def test_ro_headline_prose_matches_parquet_total_to_one_decimal() -> None:
    """D-(Headline £67bn update discipline): prose GBP bn == parquet sum to 1dp."""
    if not ANNUAL_SUMMARY_PARQUET.exists():
        pytest.skip(
            "data/derived/ro/annual_summary.parquet absent — "
            "Wave 3 rebuild_derived() has not run yet"
        )
    parquet_bn = _parquet_gb_total_gbp_bn()
    prose_bn = _prose_headline_gbp_bn()
    assert prose_bn is not None, (
        "No '£NN.N bn' headline figure found in first 40 lines of "
        "docs/schemes/ro.md — rewrite MUST include a computed GBP-bn "
        "headline in the lead paragraph."
    )
    assert prose_bn == parquet_bn, (
        f"Headline figure mismatch: prose says £{prose_bn}bn, "
        f"annual_summary.parquet GB-sum is £{parquet_bn}bn. "
        f"Either update the prose OR record a CHANGES.md "
        f"## Methodology versions entry explaining the divergence."
    )
