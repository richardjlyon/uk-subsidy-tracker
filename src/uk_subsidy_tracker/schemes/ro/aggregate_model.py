"""RO aggregate-grain pipeline — Ofgem aggregates -> annual_summary + by_technology Parquet.

Determinism discipline (D-21): no datetime.now(), no time.time(), no randomness.
Every groupby passes sort=True explicitly. Column order = Pydantic row model field
declaration order (D-10). Final sort keys are explicit and stable.

Dormancy note (D-08): this module is the active aggregate-grain path while
DORMANT_STATION_LEVEL=True in schemes/ro/__init__.py. Station-level grains
(station_month, by_allocation_round, forward_projection) are skipped until
backlog 999.1 re-activates them.

Sources consumed:
  - data/raw/ofgem/ro-generation.csv          (12-year XLSX monthly aggregate SY5-SY17)
  - data/raw/ofgem/ro-annual-aggregate.csv    (SY18-SY23 annual totals from XLSX companions)
  - data/raw/ofgem/roc-prices.csv             (buyout + recycle; SY1-SY4 NaN, SY5+ present)

D-04 nullability: ro_cost_gbp_eroc is always None under aggregate grain (no per-station
e-ROC clearing dispatch available). RoAnnualSummaryRow.ro_cost_gbp_eroc = float | None.

SY17 coverage: SY17 (Apr 2018 – Mar 2019) is recovered from parse_xlsx_to_monthly()
because no XLSX dataset companion exists for SY17 (PDF-only year). The 12-year XLSX
covers SY5-SY17; ro-annual-aggregate.csv covers SY18-SY23. _unified_annual_frame()
stitches both halves so SY17 surfaces as a real annual row with real ROC counts and
real cost (SY17 falls in the SY9-SY22 exact ROC-price range).

SY1-SY4 cost NaN: roc-prices.csv has empty price columns for SY1-SY4 (2002-03 through
2005-06) — deferred-data-gated per REQUIREMENTS.md RO-04 + backlog 999.2. NaN propagates
through the multiplication (default pandas behaviour — no fillna(0)).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from uk_subsidy_tracker import DATA_DIR
from uk_subsidy_tracker.counterfactual import (
    DEFAULT_CARBON_PRICES,
    METHODOLOGY_VERSION,
    compute_counterfactual,
)
from uk_subsidy_tracker.data.ofgem_aggregate import (
    load_annual_aggregate_csv,
    load_roc_prices_csv,
    parse_xlsx_to_monthly,
)
from uk_subsidy_tracker.schemas.ro import (
    RoAnnualSummaryRow,
    RoByTechnologyRow,
    emit_schema_json,
)

# Cross-scheme shared writer — import, do NOT re-implement (D-21/D-22 contract;
# threat T-5.05-02 mitigation; PATTERNS.md documents the intentional coupling).
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _annual_counterfactual_gbp_per_mwh() -> dict[int, float]:
    """Return {calendar_year: annual-average counterfactual £/MWh}.

    Computes ``compute_counterfactual()`` daily across the gas SAP series and
    collapses to a calendar-year mean. Empty / missing years map to 0.0 at
    lookup time (caller uses ``.get(year, 0.0)``).

    Tolerates FileNotFoundError for the ONS gas SAP XLSX on a fresh clone
    (bootstrap scenario). Any other exception propagates — silencing it
    would mask a legitimate pipeline failure and inflate the premium headline.
    """
    try:
        cf = compute_counterfactual(carbon_prices=DEFAULT_CARBON_PRICES)
    except FileNotFoundError:
        return {}
    if cf is None or cf.empty:
        return {}
    cf = cf.copy()
    cf["year"] = cf["date"].dt.year.astype(int)
    annual = cf.groupby("year", sort=True)["counterfactual_total"].mean()
    return {int(y): float(v) for y, v in annual.items()}


def _obligation_year_to_end_year(s: str) -> int:
    """Parse an obligation_year string to its end calendar year.

    Examples:
      "2019-20" → 2020
      "2023-24" → 2024
      "2006-07" → 2007
    """
    # Format is "YYYY-YY" where the end year is YYYY+1.
    parts = s.split("-")
    start = int(parts[0])
    return start + 1


def _end_year_to_obligation_year(year: int) -> str:
    """Convert an end calendar year to the obligation_year string for roc-prices join.

    Examples:
      2020 → "2019-20"
      2007 → "2006-07"
    """
    start = year - 1
    return f"{start}-{str(year)[-2:]}"


def _unified_annual_frame() -> pd.DataFrame:
    """Merge the XLSX monthly aggregate (SY5-SY17) with the XLSX-emitted
    SY18-SY23 annual aggregate into a single long-form frame keyed on
    (year, country, technology).

    SY17 coverage: SY17 (2018-19 = calendar 2018 Apr–Dec + calendar 2019
    Jan–Mar) is surfaced from the 12-year XLSX's monthly aggregate (per
    revised Plan 02, the annual-aggregate CSV starts at SY18). This
    closes the SY17 gap that would otherwise break REF 22-year
    reconciliation in Wave 6.

    SY1-SY4 cost NaN: roc-prices.csv rows for SY1-SY4 (2002-03 through
    2005-06) have empty buyout + recycle columns. NaN propagates naturally
    through rocs_issued × price multiplication — we do NOT fillna(0).
    Documented comment at the join site in build_annual_summary_aggregate.
    """
    monthly = parse_xlsx_to_monthly().copy()

    # Derive scheme_year_int per monthly row.
    # Scheme years run Apr–Mar: month >= 4 belongs to the year's SY start
    # (e.g. Apr 2018 → SY17 which starts 2018-04); month < 4 belongs to the
    # previous start year (e.g. Jan 2019 → SY17 which ends 2019-03).
    # SY number = calendar year of Apr start - 2001.
    # Apr 2018 → start 2018 → SY = 2018 - 2001 = 17.
    # Jan 2019 → start 2018 → SY = 2018 - 2001 = 17 (Jan is in same SY17).
    monthly["scheme_year_int"] = monthly.apply(
        lambda r: int(r["year"]) - 2001 if int(r["month"]) >= 4 else int(r["year"]) - 2002,
        axis=1,
    )
    # Select SY <= 17: the XLSX covers SY5-SY17; SY18+ comes from the annual
    # aggregate CSV (six XLSX dataset companions, SY18-SY23).
    xlsx_monthly_pre_sy18 = monthly[monthly["scheme_year_int"] <= 17].copy()

    pre_sy18 = (
        xlsx_monthly_pre_sy18
        .groupby(["scheme_year_int", "country", "technology"], sort=True, as_index=False)
        .agg({"rocs_issued": "sum"})
    )

    # Map SY number to end calendar year: SY N ends in year 2002 + N.
    # SY5 → 2007, SY17 → 2019.
    pre_sy18["year"] = pre_sy18["scheme_year_int"].apply(lambda n: 2002 + int(n))
    pre_sy18["scheme_year"] = pre_sy18["scheme_year_int"].apply(lambda n: f"SY{int(n):02d}")
    pre_sy18["generation_gwh"] = None   # 12-year XLSX has ROC counts only (no MWh)
    pre_sy18["ro_cost_gbp_nominal"] = None
    pre_sy18["source_pdf_url"] = None
    pre_sy18 = pre_sy18[[
        "scheme_year", "year", "country", "technology",
        "generation_gwh", "rocs_issued", "ro_cost_gbp_nominal", "source_pdf_url",
    ]]

    annual = load_annual_aggregate_csv().copy()
    # annual already has generation_gwh (GWh), rocs_issued
    annual = annual[[
        "scheme_year", "year", "country", "technology",
        "generation_gwh", "rocs_issued", "ro_cost_gbp_nominal", "source_pdf_url",
    ]]

    unified = pd.concat([pre_sy18, annual], ignore_index=True)
    # Drop duplicates preferring later data (annual CSV for any overlap; there should be none
    # since XLSX covers SY<=17 and annual CSV covers SY18+).
    unified = unified.drop_duplicates(
        subset=["scheme_year", "country", "technology"], keep="last"
    )
    return (
        unified
        .sort_values(["year", "country", "technology"], kind="mergesort")
        .reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Public build functions
# ---------------------------------------------------------------------------


def build_annual_summary_aggregate(output_dir: Path) -> pd.DataFrame:
    """Build annual_summary.parquet from Ofgem aggregates (D-04 nullable eroc).

    Pure function of data/raw/ofgem/ + data/raw/ons/ content (D-21) — no
    clock, no randomness. Column order = RoAnnualSummaryRow field
    declaration order (D-10). Final stable sort: (year, country).

    SY1-SY4 cost NaN rationale: roc-prices.csv has empty buyout + recycle
    columns for obligation years 2002-03 through 2005-06 (deferred-data-gated
    per REQUIREMENTS.md RO-04 + backlog 999.2). NaN propagates through
    rocs_issued × buyout_gbp_per_roc — we do NOT fillna(0) for these rows.
    The annual_summary.parquet rows for years 2003-2006 will have
    ro_cost_gbp = NaN, consistent with the documented data-gap rationale.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    unified = _unified_annual_frame()
    prices = load_roc_prices_csv().copy()

    # Add end calendar year for the join: obligation_year "YYYY-YY" → end year.
    prices["year"] = prices["obligation_year"].apply(_obligation_year_to_end_year)

    # Aggregate to (year, country) — generation in MWh, rocs_issued summed.
    # generation_gwh may be None for pre-SY18 rows (12-year XLSX has no MWh).
    by_yc = (
        unified
        .assign(
            generation_mwh=lambda df: pd.to_numeric(df["generation_gwh"], errors="coerce") * 1000.0,
        )
        .groupby(["year", "country"], sort=True, as_index=False)
        .agg(
            generation_mwh=("generation_mwh", "sum"),
            rocs_issued=("rocs_issued", "sum"),
        )
    )

    # Join ROC prices on end calendar year.
    by_yc = by_yc.merge(
        prices[["year", "buyout_gbp_per_roc", "recycle_gbp_per_roc", "mutualisation_gbp_total"]],
        on="year",
        how="left",
    )

    # Compute primary cost: rocs_issued × (buyout + recycle).
    # SY1-SY4: buyout + recycle are NaN → ro_cost_gbp propagates NaN (D-04 SY1-SY4 gap).
    by_yc["ro_cost_gbp"] = (
        by_yc["rocs_issued"] * (
            by_yc["buyout_gbp_per_roc"].astype(float) +
            by_yc["recycle_gbp_per_roc"].astype(float)
        )
    )

    # Mutualisation total — null for years without it.
    by_yc["mutualisation_gbp"] = pd.to_numeric(
        by_yc["mutualisation_gbp_total"], errors="coerce"
    )

    # Gas counterfactual using annual-average CY lookup.
    cf = _annual_counterfactual_gbp_per_mwh()
    by_yc["gas_counterfactual_gbp"] = by_yc.apply(
        lambda r: (
            cf.get(int(r["year"]), 0.0) * float(r["generation_mwh"])
            if pd.notna(r["generation_mwh"]) and float(r["generation_mwh"]) > 0
            else 0.0
        ),
        axis=1,
    )

    # premium = cost - counterfactual; preserves NaN when ro_cost_gbp is NaN.
    by_yc["premium_gbp"] = by_yc["ro_cost_gbp"] - by_yc["gas_counterfactual_gbp"]

    # e-ROC sensitivity is always None under aggregate grain (D-04).
    by_yc["ro_cost_gbp_eroc"] = None
    by_yc["ro_generation_mwh"] = by_yc["generation_mwh"]
    by_yc["methodology_version"] = METHODOLOGY_VERSION

    columns = list(RoAnnualSummaryRow.model_fields.keys())
    df = (
        by_yc[columns]
        .sort_values(["year", "country"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "annual_summary.parquet")
    emit_schema_json(RoAnnualSummaryRow, output_dir / "annual_summary.schema.json")
    return df


def build_by_technology_aggregate(output_dir: Path) -> pd.DataFrame:
    """Build by_technology.parquet from Ofgem aggregates (D-12 GB-only scope).

    Pure function of data/raw/ofgem/ + data/raw/ons/ content (D-21) — no
    clock, no randomness. Column order = RoByTechnologyRow field declaration
    order (D-10). Final stable sort: (year, technology).

    Aggregates over (year, technology) across GB + NI rows in _unified_annual_frame
    to match what station-level would produce (scheme-wide technology totals).
    ro_cost_gbp_eroc = None for all rows (aggregate-grain, D-04).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    unified = _unified_annual_frame()
    prices = load_roc_prices_csv().copy()
    prices["year"] = prices["obligation_year"].apply(_obligation_year_to_end_year)

    # Aggregate to (year, technology) — all countries combined.
    by_yt = (
        unified
        .assign(
            generation_mwh=lambda df: pd.to_numeric(df["generation_gwh"], errors="coerce") * 1000.0,
        )
        .groupby(["year", "technology"], sort=True, as_index=False)
        .agg(
            generation_mwh=("generation_mwh", "sum"),
            rocs_issued=("rocs_issued", "sum"),
        )
    )

    # Join ROC prices on end calendar year.
    by_yt = by_yt.merge(
        prices[["year", "buyout_gbp_per_roc", "recycle_gbp_per_roc"]],
        on="year",
        how="left",
    )

    # Compute primary cost (NaN propagates for SY1-SY4 per plan spec).
    by_yt["ro_cost_gbp"] = (
        by_yt["rocs_issued"] * (
            by_yt["buyout_gbp_per_roc"].astype(float) +
            by_yt["recycle_gbp_per_roc"].astype(float)
        )
    )

    # e-ROC sensitivity is always None under aggregate grain (D-04).
    by_yt["ro_cost_gbp_eroc"] = None
    by_yt["ro_generation_mwh"] = by_yt["generation_mwh"]
    by_yt["methodology_version"] = METHODOLOGY_VERSION

    columns = list(RoByTechnologyRow.model_fields.keys())
    df = (
        by_yt[columns]
        .sort_values(["year", "technology"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "by_technology.parquet")
    emit_schema_json(RoByTechnologyRow, output_dir / "by_technology.schema.json")
    return df
