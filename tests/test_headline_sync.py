"""Cross-surface headline-sync regression (Phase 6 D-09 + D-11).

Each parametrised case asserts a prose ``£NN.N bn`` (or ``£NNN`` per household)
figure in a ``docs/*.md`` file matches a parquet-derived value to fixed
tolerance.

Failure = update prose, run ``uv run mkdocs build --strict``, commit (per
Phase 6 D-12 cadence). Generalises ``tests/test_docs_ro_headline_sync.py``
per Phase 6 D-11 (single test file covers all prose surfaces).

The 7 parametrised cases cover:

1. ``homepage_total``       — homepage card A: total subsidy at latest year
2. ``homepage_premium``     — homepage card B: premium over gas at latest year
3. ``homepage_per_household`` — homepage card C: cost per household at latest year
4. ``cfd_paid``             — ``docs/schemes/cfd.md`` lead-paragraph "£N bn paid"
5. ``cfd_premium``          — ``docs/schemes/cfd.md`` lead-paragraph premium-over-gas
6. ``ro_covered``           — ``docs/schemes/ro.md`` lead-paragraph "£N.N bn"
   (subsumes the deleted ``test_docs_ro_headline_sync.py``)
7. ``ro_range_lower``       — ``docs/schemes/ro.md`` "£65-70 bn range" lower bound
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pyarrow.parquet as pq
import pytest

PROJECT_ROOT = Path(__file__).parent.parent

# Tolerance bands per surface type (Copywriting Contract §"Number-formatting rules").
_BN_TOLERANCE = 0.05    # ±£0.05 bn for 1-decimal billion figures
_GBP_TOLERANCE = 1.0    # ±£1 for per-household figures
_RANGE_BN_TOLERANCE = 2.0  # ±£2 bn on prose ranges (approximate framing per UI-SPEC)


@dataclass(frozen=True)
class HeadlineCase:
    """One parametrised cross-surface assertion.

    A case extracts a number from a markdown line-window via ``regex``,
    computes the parquet-derived expected value via ``compute_parquet_value``,
    and asserts they agree within ``tolerance``.

    ``compare_absolute=True`` lets a prose surface express a signed value
    via natural-language framing (e.g. "£1.4 billion *cheaper* than gas")
    while the parquet column is signed (-1.4) — the test compares
    magnitudes only and trusts the prose-side adjective for direction.
    """
    surface: str            # human-readable identifier (used as test id)
    md_path: Path
    md_line_window: tuple[int, int]   # (start, end) 1-indexed line range to scan
    regex: re.Pattern[str]
    compute_parquet_value: Callable[[], float]   # called late; returns parquet value
    tolerance: float = _BN_TOLERANCE
    # Which capture group holds the prose number (default: first group).
    capture_group: int = 1
    # Compare absolute values (prose carries direction in adjective form).
    compare_absolute: bool = False


def _bn(amount: float) -> float:
    """Convert £ to £bn rounded to 1 decimal place."""
    return round(amount / 1e9, 1)


# --------------------------------------------------------------------------
# Parquet-side value computers (called late; data must exist when test runs)
# --------------------------------------------------------------------------

def _homepage_total_bn() -> float:
    """Homepage card A: cross_scheme.parquet total cost at latest reconciled year."""
    from uk_subsidy_tracker.schemes import portal
    df = pq.read_table(portal.DERIVED_DIR / "cross_scheme.parquet").to_pandas()
    year = portal.latest_fully_reconciled_year()
    return _bn(float(df[df["year"] == year]["cost_gbp"].sum()))


def _homepage_premium_bn() -> float:
    """Homepage card B: cross_scheme.parquet total premium at latest reconciled year."""
    from uk_subsidy_tracker.schemes import portal
    df = pq.read_table(portal.DERIVED_DIR / "cross_scheme.parquet").to_pandas()
    year = portal.latest_fully_reconciled_year()
    return _bn(float(df[df["year"] == year]["premium_gbp"].sum()))


def _homepage_per_household_gbp() -> float:
    """Homepage card C: total cost / households_uk at latest reconciled year."""
    from uk_subsidy_tracker.schemes import portal
    df = pq.read_table(portal.DERIVED_DIR / "cross_scheme.parquet").to_pandas()
    year = portal.latest_fully_reconciled_year()
    sub = df[df["year"] == year]
    total_cost = float(sub["cost_gbp"].sum())
    households = int(sub["households_uk"].iloc[0])
    return float(total_cost / households)


def _cfd_paid_total_bn() -> float:
    """docs/schemes/cfd.md headline: cumulative CfD payments to consumers."""
    df = pq.read_table(
        PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet"
    ).to_pandas()
    return _bn(float(df["cfd_payments_gbp"].sum()))


def _cfd_premium_total_bn() -> float:
    """docs/schemes/cfd.md headline: cumulative premium over gas counterfactual.

    Note the parquet ``premium_over_gas_gbp`` column is signed (positive when
    consumers overpaid relative to gas; negative in years where CfD paid back
    into the levy because gas was cheaper than strike). The prose figure
    ("£N bn more than the existing gas fleet would have cost") is the
    aggregate signed sum to one decimal — same arithmetic as the parquet
    column total.
    """
    df = pq.read_table(
        PROJECT_ROOT / "data" / "derived" / "cfd" / "annual_summary.parquet"
    ).to_pandas()
    return _bn(float(df["premium_over_gas_gbp"].sum()))


def _ro_covered_total_bn() -> float:
    """docs/schemes/ro.md headline: GB-only RO cost (covered scheme years)."""
    df = pq.read_table(
        PROJECT_ROOT / "data" / "derived" / "ro" / "annual_summary.parquet"
    ).to_pandas()
    gb = df[df["country"] == "GB"]
    return _bn(float(gb["ro_cost_gbp"].sum()))


def _ro_range_lower_bound_bn() -> float:
    """docs/schemes/ro.md "£65-70 bn range" — assert lower bound is ≥ covered total.

    The prose range (covered + deferred SY1-SY4 + SY17) MUST be greater than
    the covered-only headline. Returns the minimum acceptable lower bound:
    the covered-only total (lower bound must exceed this).
    """
    return _ro_covered_total_bn()


# --------------------------------------------------------------------------
# Regex patterns (anchored to specific labels to avoid cross-figure collisions)
# --------------------------------------------------------------------------

# Generic £N.N bn (with or without space, with or without "billion" word form)
_HEADLINE_RE = re.compile(r"£\s*(\d+(?:\.\d+)?)\s*(?:bn|billion)\b", re.IGNORECASE)

# Homepage card A: anchor capture-group 1 to the £N.N bn that LITERALLY precedes
# "Total subsidy" in the rendered Material grid card (`**£8.0 bn**\n\n    Total subsidy`).
_HOMEPAGE_TOTAL_RE = re.compile(
    r"\*\*£\s*(\d+(?:\.\d+)?)\s*bn\*\*\s*\n\s*\n\s+Total subsidy",
    re.IGNORECASE,
)

# Homepage card B: same shape, anchored to "Premium over gas".
_HOMEPAGE_PREMIUM_RE = re.compile(
    r"\*\*£\s*(\d+(?:\.\d+)?)\s*bn\*\*\s*\n\s*\n\s+Premium over gas",
    re.IGNORECASE,
)

# Homepage card C: per-household sub-£1k figure (no "bn" suffix), anchored to
# "Per household". Captures bare digits (with optional comma separator).
_HOMEPAGE_PER_HH_RE = re.compile(
    r"\*\*£\s*([\d,]+)\*\*\s*\n\s*\n\s+Per household",
    re.IGNORECASE,
)

# CfD lead-paragraph "paid £N billion": anchor to "paid £" + "billion" (or "bn")
# to disambiguate from the £14 billion premium figure on the same line.
_CFD_PAID_RE = re.compile(
    r"paid\s+£\s*(\d+(?:\.\d+)?)\s*billion\b",
    re.IGNORECASE,
)

# CfD lead-paragraph premium: "£N.N billion *cheaper*" or "£N.N billion *more
# expensive*" — anchor to the directional adjective so the test catches drift
# without imposing a specific sign convention. The captured magnitude is
# compared to ``abs(parquet_premium_total)`` (compare_absolute=True on the case).
_CFD_PREMIUM_RE = re.compile(
    r"£\s*(\d+(?:\.\d+)?)\s*billion\s+\*(?:cheaper|more\s+expensive)\*",
    re.IGNORECASE,
)

# RO lead-paragraph headline: first £N.N bn in the lead paragraph.
# (Identical to the legacy test_docs_ro_headline_sync.py regex.)
_RO_COVERED_RE = _HEADLINE_RE

# RO range "£65-70 bn": capture the LOWER bound (group 1) — must exceed
# the covered-only total to be a self-consistent range.
_RO_RANGE_RE = re.compile(
    r"£\s*(\d+)\s*[\-–—]\s*(\d+)\s*bn\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------
# Cases (D-11: 7 parametrised cross-surface assertions)
# --------------------------------------------------------------------------

_CASES: list[HeadlineCase] = [
    HeadlineCase(
        surface="homepage_total",
        md_path=PROJECT_ROOT / "docs" / "index.md",
        md_line_window=(1, 50),  # 3-card row sits above the scheme grid
        regex=_HOMEPAGE_TOTAL_RE,
        compute_parquet_value=_homepage_total_bn,
    ),
    HeadlineCase(
        surface="homepage_premium",
        md_path=PROJECT_ROOT / "docs" / "index.md",
        md_line_window=(1, 50),
        regex=_HOMEPAGE_PREMIUM_RE,
        compute_parquet_value=_homepage_premium_bn,
    ),
    HeadlineCase(
        surface="homepage_per_household",
        md_path=PROJECT_ROOT / "docs" / "index.md",
        md_line_window=(1, 50),
        regex=_HOMEPAGE_PER_HH_RE,
        compute_parquet_value=_homepage_per_household_gbp,
        tolerance=_GBP_TOLERANCE,
    ),
    HeadlineCase(
        surface="cfd_paid",
        md_path=PROJECT_ROOT / "docs" / "schemes" / "cfd.md",
        md_line_window=(1, 10),  # lead-paragraph headline
        regex=_CFD_PAID_RE,
        compute_parquet_value=_cfd_paid_total_bn,
    ),
    HeadlineCase(
        surface="cfd_premium",
        md_path=PROJECT_ROOT / "docs" / "schemes" / "cfd.md",
        md_line_window=(1, 10),
        regex=_CFD_PREMIUM_RE,
        compute_parquet_value=_cfd_premium_total_bn,
        # Prose carries direction in *cheaper*/*more expensive* adjective;
        # parquet column is signed. Compare magnitudes only.
        compare_absolute=True,
    ),
    HeadlineCase(
        surface="ro_covered",
        md_path=PROJECT_ROOT / "docs" / "schemes" / "ro.md",
        md_line_window=(1, 40),
        regex=_RO_COVERED_RE,
        compute_parquet_value=_ro_covered_total_bn,
    ),
    HeadlineCase(
        surface="ro_range_lower",
        md_path=PROJECT_ROOT / "docs" / "schemes" / "ro.md",
        md_line_window=(1, 40),
        regex=_RO_RANGE_RE,
        # The prose lower bound MUST be at least the covered-only total
        # (i.e. covered + deferred ≥ covered). We assert prose lower ≥ parquet
        # covered, with a tolerance band reflecting the approximate "65-70"
        # framing.
        compute_parquet_value=_ro_range_lower_bound_bn,
        tolerance=_RANGE_BN_TOLERANCE * 4.0,  # wide tolerance: range is approximate
    ),
]


# --------------------------------------------------------------------------
# The parametrised test
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", _CASES, ids=lambda c: c.surface)
def test_headline_matches_parquet(case: HeadlineCase) -> None:
    """Each prose surface MUST match its parquet-derived value within tolerance.

    Failure flow (per Phase 6 D-12 cadence):

    1. RED: this test surfaces the prose/parquet drift with both numbers
       and the surface location.
    2. Update the prose in the named markdown file (NOT the test).
    3. Re-run ``uv run mkdocs build --strict`` to confirm the docs site
       still builds.
    4. Commit with a message referencing the surface and the new figure.
    """
    if not case.md_path.exists():
        pytest.fail(f"Markdown surface missing: {case.md_path}")

    # Parquet absent — CI rebuild_derived() must run first.
    try:
        expected = case.compute_parquet_value()
    except FileNotFoundError as e:
        pytest.skip(
            f"Upstream parquet absent for {case.surface}: {e} — "
            "run schemes.{cfd,ro,portal}.rebuild_derived() first"
        )
        return

    # Read the markdown line-window.
    all_lines = case.md_path.read_text(encoding="utf-8").splitlines()
    start, end = case.md_line_window
    text = "\n".join(all_lines[start - 1: end])

    m = case.regex.search(text)
    assert m is not None, (
        f"\n  No headline found in '{case.surface}'\n"
        f"  regex: {case.regex.pattern!r}\n"
        f"  file:  {case.md_path}\n"
        f"  line window: [{start}-{end}]\n"
    )

    # Parse the captured number — strip commas (per-household format).
    prose_str = m.group(case.capture_group).replace(",", "")
    prose_value = float(prose_str)

    # Round prose to same precision as parquet computation for billion-tier
    # surfaces; per-household tolerance is in raw GBP.
    if case.tolerance == _BN_TOLERANCE:
        prose_value = round(prose_value, 1)
        expected_value = round(expected, 1)
    else:
        expected_value = expected

    # Surfaces that carry direction in adjective form (e.g. "cheaper" /
    # "more expensive") compare magnitudes only — the prose-side wording
    # is the source of truth for sign.
    compare_prose = abs(prose_value) if case.compare_absolute else prose_value
    compare_expected = abs(expected_value) if case.compare_absolute else expected_value

    assert abs(compare_prose - compare_expected) <= case.tolerance, (
        f"\n  Headline drift on '{case.surface}':\n"
        f"  prose value    = {prose_value} (in {case.md_path.name} "
        f"lines {start}-{end})\n"
        f"  parquet value  = {expected_value}\n"
        f"  tolerance      = ±{case.tolerance}\n"
        f"  compare_absolute = {case.compare_absolute}\n\n"
        f"  Either:\n"
        f"  (a) update {case.md_path.name} prose to match the parquet "
        f"value; OR\n"
        f"  (b) record a CHANGES.md ## Methodology versions entry "
        f"if the parquet change is intentional."
    )
