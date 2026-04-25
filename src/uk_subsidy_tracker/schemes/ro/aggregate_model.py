"""RO aggregate-grain pipeline — Ofgem aggregates -> annual_summary + by_technology Parquet.

Determinism discipline (D-21): no datetime.now(), no time.time(), no randomness.
Every groupby passes sort=True explicitly. Column order = Pydantic row model field
declaration order (D-10). Final sort keys are explicit and stable.

Dormancy note (D-08): this module is the active aggregate-grain path while
DORMANT_STATION_LEVEL=True in schemes/ro/__init__.py. Station-level grains
(station_month, by_allocation_round, forward_projection) are skipped until
backlog 999.1 re-activates them.

Sources consumed:
  - data/raw/ofgem/ro-generation.csv          (12-year XLSX monthly aggregate SY5-SY16)
  - data/raw/ofgem/ro-annual-aggregate.csv    (SY18-SY23 annual totals from XLSX companions)
  - data/raw/ofgem/roc-prices.csv             (buyout + recycle; SY1-SY4 NaN, SY5+ present)

D-04 nullability: ro_cost_gbp_eroc is always None under aggregate grain (no per-station
e-ROC clearing dispatch available). RoAnnualSummaryRow.ro_cost_gbp_eroc = float | None.

Year convention (D-07 fix, Defect 3): the canonical `year` column uses the OBLIGATION-YEAR
START calendar year throughout — matching tests/fixtures/benchmarks.yaml::ref_constable
convention. SY5 (2006-07) → year=2006; SY18 (2019-20) → year=2019; SY23 (2024-25) → year=2024.
The ROC-price join uses a separate `obligation_end_year` column (end calendar year) to
match roc-prices.csv's obligation_year format ("YYYY-YY" → end year).

SY17 (2018-19 = start year 2018): deferred — the 12-year XLSX covers SY5-SY16 only
(Apr 2006 – Mar 2018). No XLSX dataset companion exists for SY17 (PDF-only year).
year=2018 is absent from annual_summary.parquet. Plan 06 REF reconciliation must
account for this gap.

SY1-SY4 cost NaN: roc-prices.csv has empty price columns for SY1-SY4 (2002-03 through
2005-06) — deferred-data-gated per REQUIREMENTS.md RO-04 + backlog 999.2. NaN propagates
through the multiplication (default pandas behaviour — no fillna(0)).

Defect 4 fix: ro-annual-aggregate.csv stores SY20-SY23 GB rows as 3 sub-rows per
technology (England / Scotland / Wales merged to 'GB' country code). _unified_annual_frame()
aggregates with groupby().sum() rather than drop_duplicates() to preserve all sub-rows.
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


# Canonical start-year mapping for SY18-SY23 (Defect 3 fix).
# obligation_end_year is used for the roc-prices join only;
# 'year' in output = obligation START year (matching ref_constable convention).
_SY_TO_START_YEAR: dict[str, int] = {
    "SY18": 2019, "SY19": 2020, "SY20": 2021,
    "SY21": 2022, "SY22": 2023, "SY23": 2024,
}
_SY_TO_END_YEAR: dict[str, int] = {
    "SY18": 2020, "SY19": 2021, "SY20": 2022,
    "SY21": 2023, "SY22": 2024, "SY23": 2025,
}


def _unified_annual_frame() -> pd.DataFrame:
    """Merge the XLSX monthly aggregate (SY5-SY16) with the XLSX-emitted
    SY18-SY23 annual aggregate into a single long-form frame keyed on
    (scheme_year, country, technology).

    Returns a DataFrame with columns:
      scheme_year, year (START year), obligation_end_year (for price join),
      country, technology, generation_gwh, rocs_issued,
      ro_cost_gbp_nominal, source_pdf_url.

    Year convention (Defect 3 fix): canonical 'year' = obligation-year START
    calendar year, matching ref_constable. SY5 → year=2006; SY18 → year=2019.
    A separate 'obligation_end_year' column preserves the end-year for the
    roc-prices join (roc-prices obligation_year "YYYY-YY" → end year YYYY+1).

    SY17 (year=2018): absent from both the 12-year XLSX (covers SY5-SY16
    only, Apr 2006 – Mar 2018) and ro-annual-aggregate.csv (starts at SY18).
    year=2018 will be missing from annual_summary.parquet. Documented.

    Defect 4 fix: ro-annual-aggregate.csv stores SY20-SY23 GB data as
    3 sub-rows per technology (England / Scotland / Wales each coded 'GB').
    This function aggregates via groupby().sum() — NOT drop_duplicates —
    so all sub-rows are included in the technology total.

    SY1-SY4 cost NaN: roc-prices.csv has empty price columns for SY1-SY4
    (2002-03 through 2005-06) — deferred-data-gated per REQUIREMENTS.md
    RO-04 + backlog 999.2. NaN propagates through rocs_issued × price
    multiplication; we do NOT fillna(0).
    """
    monthly = parse_xlsx_to_monthly().copy()

    # Derive scheme_year_int per monthly row.
    # Scheme years run Apr–Mar: month >= 4 belongs to the year's SY start
    # (e.g. Apr 2006 → SY5 which starts 2006-04); month < 4 belongs to the
    # previous start year (e.g. Jan 2007 → SY5 which ends 2007-03).
    # SY number = calendar year of Apr start - 2001.
    # SY5: Apr 2006 → start 2006 → SY = 2006 - 2001 = 5.
    monthly["scheme_year_int"] = monthly.apply(
        lambda r: int(r["year"]) - 2001 if int(r["month"]) >= 4 else int(r["year"]) - 2002,
        axis=1,
    )
    # Select SY <= 16: the 12-year XLSX covers SY5-SY16 (Apr 2006 – Mar 2018).
    # SY17 (Apr 2018 – Mar 2019) is absent from the XLSX and from the annual-
    # aggregate CSV (starts at SY18) — year=2018 is a known gap, documented.
    # SY18+ comes from the annual-aggregate CSV (six XLSX dataset companions).
    xlsx_monthly_pre_sy18 = monthly[monthly["scheme_year_int"] <= 16].copy()

    pre_sy18 = (
        xlsx_monthly_pre_sy18
        .groupby(["scheme_year_int", "country", "technology"], sort=True, as_index=False)
        .agg(
            generation_gwh=("generation_mwh", lambda x: x.sum(min_count=1) / 1000.0
                            if x.notna().any() else float("nan")),
            rocs_issued=("rocs_issued", "sum"),
        )
    )

    # Defect 3 fix: use START calendar year (2001 + SY_int) as canonical year.
    # SY5 → year=2006; SY16 → year=2017.
    # obligation_end_year (= 2002 + SY_int) is kept for the roc-prices join.
    pre_sy18["year"] = pre_sy18["scheme_year_int"].apply(lambda n: 2001 + int(n))
    pre_sy18["obligation_end_year"] = pre_sy18["scheme_year_int"].apply(lambda n: 2002 + int(n))
    pre_sy18["scheme_year"] = pre_sy18["scheme_year_int"].apply(lambda n: f"SY{int(n):02d}")
    # 12-year XLSX has generation_mwh = None throughout (ROC counts only,
    # no MWh data in the 'ROCs by Tech & Month' sheet). generation_gwh = NaN.
    pre_sy18["generation_gwh"] = float("nan")
    pre_sy18["ro_cost_gbp_nominal"] = None
    pre_sy18["source_pdf_url"] = None
    pre_sy18 = pre_sy18[[
        "scheme_year", "year", "obligation_end_year", "country", "technology",
        "generation_gwh", "rocs_issued", "ro_cost_gbp_nominal", "source_pdf_url",
    ]]

    annual = load_annual_aggregate_csv().copy()

    # Defect 3 fix: ro-annual-aggregate.csv uses END-year convention
    # (SY18 → year=2020). Override with START-year convention for consistency.
    annual["year"] = annual["scheme_year"].map(_SY_TO_START_YEAR)
    annual["obligation_end_year"] = annual["scheme_year"].map(_SY_TO_END_YEAR)

    # Defect 4 fix: SY20-SY23 have 3 sub-rows per (country='GB', technology)
    # because _parse_sy20_sy23 stores England/Scotland/Wales separately under
    # country='GB'. Aggregate with groupby().sum() to combine them, preserving
    # NaN only when all sub-rows are NaN (min_count=1).
    annual_agg = (
        annual
        .groupby(
            ["scheme_year", "year", "obligation_end_year", "country", "technology"],
            sort=True, as_index=False,
        )
        .agg(
            generation_gwh=("generation_gwh", lambda x: x.sum(min_count=1)),
            rocs_issued=("rocs_issued", lambda x: x.sum(min_count=1)),
            ro_cost_gbp_nominal=("ro_cost_gbp_nominal", lambda x: x.sum(min_count=1)),
            source_pdf_url=("source_pdf_url", "first"),
        )
    )

    _COLS = [
        "scheme_year", "year", "obligation_end_year", "country", "technology",
        "generation_gwh", "rocs_issued", "ro_cost_gbp_nominal", "source_pdf_url",
    ]
    unified = pd.concat([pre_sy18[_COLS], annual_agg[_COLS]], ignore_index=True)
    # No drop_duplicates: there is no overlap between XLSX (SY5-SY16) and annual CSV (SY18-SY23).
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

    Defect 3 fix: price join uses 'obligation_end_year' (not 'year') so that
    the start-year-labelled output rows correctly join to the end-year-keyed
    roc-prices.csv. Example: year=2019 (SY18 start) joins on
    obligation_end_year=2020 which maps to roc-prices row "2019-20".

    Defect 2 fix: mutualisation_gbp_total from roc-prices is a scheme-wide
    UK total. It is assigned in full to the GB row for each year; NI rows
    receive 0.0 explicitly (not NaN) to avoid double-counting. Convention
    per D-11: "RO + ROS combined per SY22 XLSX Figures A3.3 + A3.4; full
    amount carried on GB row by convention; ROS share folded in."

    SY1-SY4 cost NaN rationale: roc-prices.csv has empty buyout + recycle
    columns for obligation years 2002-03 through 2005-06 (deferred-data-gated
    per REQUIREMENTS.md RO-04 + backlog 999.2). NaN propagates through
    rocs_issued × buyout_gbp_per_roc — we do NOT fillna(0) for these rows.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    unified = _unified_annual_frame()
    prices = load_roc_prices_csv().copy()

    # Defect 3 fix: join key is obligation_end_year (end calendar year),
    # derived from roc-prices.csv obligation_year string "YYYY-YY".
    prices["obligation_end_year"] = prices["obligation_year"].apply(_obligation_year_to_end_year)

    # Aggregate to (year, obligation_end_year, country).
    # Defect 1 fix: use min_count=1 so sum() of all-NaN generation stays NaN
    # rather than collapsing to 0 (12-year XLSX has no MWh data).
    by_yc = (
        unified
        .assign(
            generation_mwh=lambda df: pd.to_numeric(df["generation_gwh"], errors="coerce") * 1000.0,
        )
        .groupby(["year", "obligation_end_year", "country"], sort=True, as_index=False)
        .agg(
            generation_mwh=("generation_mwh", lambda x: x.sum(min_count=1)),
            rocs_issued=("rocs_issued", "sum"),
        )
    )

    # Join ROC prices on obligation_end_year (Defect 3 fix).
    by_yc = by_yc.merge(
        prices[["obligation_end_year", "buyout_gbp_per_roc", "recycle_gbp_per_roc",
                "mutualisation_gbp_total"]],
        on="obligation_end_year",
        how="left",
    )

    # Compute primary cost: rocs_issued × (buyout + recycle).
    # SY1-SY4: buyout + recycle are NaN → ro_cost_gbp propagates NaN.
    by_yc["ro_cost_gbp"] = (
        by_yc["rocs_issued"] * (
            by_yc["buyout_gbp_per_roc"].astype(float) +
            by_yc["recycle_gbp_per_roc"].astype(float)
        )
    )

    # Defect 2 fix: mutualisation is a single scheme-wide total.
    # Assign full amount to GB row; NI rows get 0.0 (not NaN) to avoid
    # double-counting when aggregating across countries.
    # Convention: "scheme-wide mutualisation total carried on GB row by
    # convention; ROS share folded in per D-11."
    mut_raw = pd.to_numeric(by_yc["mutualisation_gbp_total"], errors="coerce")
    by_yc["mutualisation_gbp"] = mut_raw.where(by_yc["country"] == "GB", other=0.0)

    # Gas counterfactual using annual-average CY lookup.
    # Uses start year (= 'year' column) for the calendar-year lookup.
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
    # Defect 1 fix: preserve NaN for years with no generation data (pre-SY18).
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

    Defect 3 fix: price join uses obligation_end_year (matching the start-year
    output convention in 'year' column).
    Defect 1 fix: generation_mwh preserves NaN (min_count=1) for pre-SY18 rows.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    unified = _unified_annual_frame()
    prices = load_roc_prices_csv().copy()
    # Defect 3 fix: join key is obligation_end_year.
    prices["obligation_end_year"] = prices["obligation_year"].apply(_obligation_year_to_end_year)

    # Aggregate to (year, obligation_end_year, technology) — all countries combined.
    by_yt = (
        unified
        .assign(
            generation_mwh=lambda df: pd.to_numeric(df["generation_gwh"], errors="coerce") * 1000.0,
        )
        .groupby(["year", "obligation_end_year", "technology"], sort=True, as_index=False)
        .agg(
            generation_mwh=("generation_mwh", lambda x: x.sum(min_count=1)),
            rocs_issued=("rocs_issued", "sum"),
        )
    )

    # Join ROC prices on obligation_end_year (Defect 3 fix).
    by_yt = by_yt.merge(
        prices[["obligation_end_year", "buyout_gbp_per_roc", "recycle_gbp_per_roc"]],
        on="obligation_end_year",
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
    # Defect 1 fix: preserve NaN generation for pre-SY18 rows.
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
