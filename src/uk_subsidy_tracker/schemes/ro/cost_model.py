# dormant: true
"""RO cost model — raw Ofgem data → station_month.parquet (Plan 05-05 Task 2).

Mirrors ``schemes/cfd/cost_model.py`` with RO-specific join logic. Writes
``data/derived/ro/station_month.parquet`` + sibling ``station_month.schema.json``
via the pinned deterministic Parquet writer shared from CfD (D-21/D-22).

Per-row contract (D-01, D-02, D-05, D-08, D-09, D-11, D-12):

- ``station_id``: Ofgem accreditation number (str).
- ``country``: 'GB' or 'NI' — mapped from {England/Scotland/Wales/NI} (D-09).
- ``technology``: Ofgem ``technology_type`` (verbatim).
- ``commissioning_window``: banding-window label (pre-2013, 2013/14, ...).
- ``month_end``: ``output_period_end`` snapped to month end.
- ``obligation_year``: Apr-Mar obligation-year START year as int64 (e.g. 2021
  represents OY 2021-22). Joined to ``roc-prices.csv`` via the string label
  "YYYY-YY" internally, then converted to int (D-08 + schema D-10).
- ``generation_mwh``: from ``ro-generation.csv`` (Ofgem monthly).
- ``rocs_issued``: Ofgem-published primary (D-01 short-circuits R1).
- ``rocs_computed``: ``generation_mwh × banding_factor_yaml`` — audit cross-check.
- ``banding_factor_yaml``: ``RoBandingTable.lookup()`` result.
- ``ro_cost_gbp``: ``rocs_issued × (buyout + recycle) + mutualisation_gbp`` (D-02 primary).
- ``ro_cost_gbp_eroc``: ``rocs_issued × eroc_clearing`` (D-02 sensitivity).
- ``ro_cost_gbp_nocarbon``: equals ``ro_cost_gbp`` by construction for RO
  because ROC price is legislatively fixed (buyout + recycle) and carries no
  carbon component. Column kept for schema parity with schemes that DO embed
  carbon (future FiT export tariff); researchers filtering
  ``ro_cost_gbp_nocarbon == ro_cost_gbp`` get a definitive signal. (D-05.)
- ``gas_counterfactual_gbp``: ``generation_mwh × annual_avg_counterfactual[year]``
  where the annual average is the mean of ``compute_counterfactual()``'s daily
  ``counterfactual_total`` grouped by calendar year. Shared gas counterfactual
  per ARCHITECTURE §6.2.
- ``premium_gbp``: ``ro_cost_gbp - gas_counterfactual_gbp``.
- ``mutualisation_gbp``: ``rocs_issued × mutualisation_gbp_per_roc`` (null
  except OY 2021-22 per D-11 — carried by the roc-prices CSV).
- ``methodology_version``: ``counterfactual.METHODOLOGY_VERSION`` (D-12 / GOV-02).

D-03 contract: this is the canonical station × month derivation. All rollups
in ``aggregation.py`` re-read ``station_month.parquet``; they do NOT take an
in-memory DataFrame argument.

Determinism discipline (D-21): no ``datetime.now()``, no ``time.time()``, no
randomness; every ``groupby(sort=True)`` explicit; final sort on
``(station_id, month_end)``.

Dormancy:
    This module is dormant per Phase 05.2 (RO Data Reconstruction — Aggregate
    Grain). Station-level code paths are preserved in-tree but not exercised
    by the aggregate pipeline (schemes.ro.DORMANT_STATION_LEVEL = True).
    Re-activated on backlog 999.1 (Credentialed RER Access Automation) by
    flipping DORMANT_STATION_LEVEL to False and removing the per-test
    @pytest.mark.dormant marks.

    Design note: .planning/notes/ro-data-strategy-option-a1.md
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pandera.pandas as pa

from uk_subsidy_tracker.counterfactual import (
    DEFAULT_CARBON_PRICES,
    METHODOLOGY_VERSION,
    compute_counterfactual,
)
from uk_subsidy_tracker.data.ofgem_ro import (
    load_ofgem_ro_generation,
    load_ofgem_ro_register,
)
from uk_subsidy_tracker.data.ro_bandings import load_ro_bandings
from uk_subsidy_tracker.data.roc_prices import load_roc_prices
from uk_subsidy_tracker.schemas.ro import RoStationMonthRow, emit_schema_json

# Cross-scheme shared writer — import, do NOT re-implement (D-21/D-22 contract;
# threat T-5.05-02 mitigation; PATTERNS.md documents the intentional coupling).
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet

# Loader-owned pandera schema; every column matches RoStationMonthRow fields.
station_month_schema = pa.DataFrameSchema(
    {
        "station_id": pa.Column(str, coerce=True),
        "country": pa.Column(str, checks=pa.Check.isin(["GB", "NI"])),
        "technology": pa.Column(str, coerce=True),
        "commissioning_window": pa.Column(str, coerce=True),
        "month_end": pa.Column("datetime64[ns]", coerce=True),
        "obligation_year": pa.Column("int64", coerce=True),
        "generation_mwh": pa.Column(float, coerce=True),
        "rocs_issued": pa.Column(float, coerce=True),
        "rocs_computed": pa.Column(float, nullable=True, coerce=True),
        "banding_factor_yaml": pa.Column(float, nullable=True, coerce=True),
        "ro_cost_gbp": pa.Column(float, coerce=True),
        "ro_cost_gbp_eroc": pa.Column(float, coerce=True),
        "ro_cost_gbp_nocarbon": pa.Column(float, coerce=True),
        "gas_counterfactual_gbp": pa.Column(float, coerce=True),
        "premium_gbp": pa.Column(float, coerce=True),
        "mutualisation_gbp": pa.Column(float, nullable=True, coerce=True),
        "methodology_version": pa.Column(str),
    },
    strict=False,
    coerce=True,
)


def _obligation_year_start(month_end: pd.Timestamp) -> int:
    """Return the obligation-year START year containing ``month_end`` (D-08).

    March month_end → previous OY (ends Mar 31). April month_end → new OY.
    OY 2021-22 is represented as the integer 2021 on the Parquet row
    (matches ``RoStationMonthRow.obligation_year: int``).
    """
    ts = pd.Timestamp(month_end)
    return int(ts.year) if ts.month >= 4 else int(ts.year) - 1


def _obligation_year_label(start_year: int) -> str:
    """Format OY start-year integer as the 'YYYY-YY' string used in roc-prices.csv."""
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def _commissioning_window_label(commissioning_date) -> str:
    """REF Table 1 window label. NaT / pre-2013 → 'pre-2013'; else 'YYYY/YY'."""
    if commissioning_date is None or pd.isna(commissioning_date):
        return "pre-2013"
    ts = pd.Timestamp(commissioning_date)
    if ts < pd.Timestamp("2013-04-01"):
        return "pre-2013"
    start_year = ts.year if ts.month >= 4 else ts.year - 1
    return f"{start_year}/{str(start_year + 1)[-2:]}"


def _annual_counterfactual_gbp_per_mwh() -> dict[int, float]:
    """Return {calendar_year: annual-average counterfactual £/MWh}.

    Computes ``compute_counterfactual()`` daily across the gas SAP series and
    collapses to a calendar-year mean. Empty / missing years map to 0.0 at
    lookup time (no key raises KeyError — caller uses ``.get(year, 0.0)``).

    Shared CfD/RO counterfactual per ARCHITECTURE §6.2 + counterfactual.py
    signature: ``compute_counterfactual(carbon_prices=DEFAULT_CARBON_PRICES)``
    returns a daily DataFrame with ``counterfactual_total`` (£/MWh).
    """
    try:
        cf = compute_counterfactual(carbon_prices=DEFAULT_CARBON_PRICES)
    except FileNotFoundError:
        # Only tolerate the one expected bootstrap failure: ONS gas SAP XLSX
        # not yet downloaded (Wave-2 smoke on a fresh clone). In that case
        # return an empty lookup so cost_model emits zero
        # gas_counterfactual_gbp, which validate() Check 2 surfaces via the
        # REF-drift warner. Any other exception (pandera schema drift, missing
        # columns from upstream refactors, arithmetic errors) is a real bug
        # and MUST propagate — silencing it would mask a legitimate failure
        # and silently inflate the subsidy-premium headline figure.
        return {}
    if cf is None or cf.empty:
        return {}
    cf = cf.copy()
    cf["year"] = cf["date"].dt.year.astype(int)
    annual = cf.groupby("year", sort=True)["counterfactual_total"].mean()
    return {int(y): float(v) for y, v in annual.items()}


def build_station_month(output_dir: Path) -> pd.DataFrame:
    """Build and persist ``station_month.parquet`` + ``station_month.schema.json``.

    Pure function of ``data/raw/ofgem/`` + ``data/raw/ons/`` content (D-21) —
    no clock, no randomness. Column order = ``RoStationMonthRow`` field
    declaration order (D-10).

    Parameters
    ----------
    output_dir
        Directory into which the Parquet + schema.json are written. Caller
        (``rebuild_derived``) creates the directory; this function does the
        same defensively.

    Returns
    -------
    pd.DataFrame
        The in-memory DataFrame written to Parquet. Returned so tests can
        inspect without re-reading from disk.
    """
    # --------------------------------------------------------------
    # 1. Load raw inputs (each loader runs pandera validation inside).
    # --------------------------------------------------------------
    gen = load_ofgem_ro_generation()
    reg = load_ofgem_ro_register()
    prices = load_roc_prices()
    bandings = load_ro_bandings()

    # Empty-input short-circuit: when the Option-D stubs carry zero data rows
    # (Wave-2 smoke scenario), produce an empty Parquet with the correct
    # schema so downstream rollups + tests see the canonical shape.
    empty = len(gen) == 0

    # --------------------------------------------------------------
    # 2. Merge generation (monthly) with register (per-station metadata).
    # --------------------------------------------------------------
    reg_cols = ["station_id", "technology_type", "country", "commissioning_date"]
    # Defensive: missing columns in the stub register DataFrame coerce to NaN.
    for col in reg_cols:
        if col not in reg.columns:
            reg[col] = pd.Series(dtype="object")
    df = gen.merge(
        reg[reg_cols],
        on="station_id",
        how="left",
    ).rename(columns={"technology_type": "technology"})

    # --------------------------------------------------------------
    # 3. Month-end anchor + obligation_year (int start-year) (D-08).
    # --------------------------------------------------------------
    if empty:
        # Guarantee the expected dtype on empty DataFrames so pandera coerce
        # can succeed on a zero-row frame.
        df["month_end"] = pd.to_datetime(pd.Series([], dtype="object"))
        df["obligation_year"] = pd.Series([], dtype="int64")
        df["_oy_label"] = pd.Series([], dtype="object")
    else:
        df["month_end"] = pd.to_datetime(df["output_period_end"]) + pd.offsets.MonthEnd(0)
        df["obligation_year"] = df["month_end"].apply(_obligation_year_start).astype("int64")
        df["_oy_label"] = df["obligation_year"].apply(_obligation_year_label)

    # --------------------------------------------------------------
    # 4. Country normalisation (D-09).
    # --------------------------------------------------------------
    country_map = {
        "England": "GB",
        "Scotland": "GB",
        "Wales": "GB",
        "GB": "GB",
        "Northern Ireland": "NI",
        "NI": "NI",
    }
    df["country"] = df["country"].map(country_map).fillna("GB")

    # --------------------------------------------------------------
    # 5. Commissioning-window label (for by_allocation_round rollup).
    # --------------------------------------------------------------
    if empty:
        df["commissioning_window"] = pd.Series([], dtype="object")
    else:
        df["commissioning_window"] = df["commissioning_date"].apply(
            _commissioning_window_label
        )

    # --------------------------------------------------------------
    # 6. Banding lookup (D-01 audit cross-check). On empty, short-circuit.
    # --------------------------------------------------------------
    if empty:
        df["banding_factor_yaml"] = pd.Series([], dtype="float64")
        df["rocs_computed"] = pd.Series([], dtype="float64")
    else:
        def _lookup_banding(row):
            cd = row.get("commissioning_date")
            if cd is None or pd.isna(cd):
                # No commissioning date → cannot look up; leave NaN rather than
                # fabricate a date (audit transparency per D-04 Check 1).
                return float("nan")
            try:
                return bandings.lookup(
                    technology=row["technology"],
                    country=row["country"],
                    commissioning_date=pd.Timestamp(cd).date(),
                )
            except (KeyError, TypeError, ValueError):
                return float("nan")

        df["banding_factor_yaml"] = df.apply(_lookup_banding, axis=1)
        df["rocs_computed"] = df["generation_mwh"] * df["banding_factor_yaml"]

    # --------------------------------------------------------------
    # 7. Join roc-prices on obligation-year string label.
    # --------------------------------------------------------------
    # roc-prices.csv keys obligation_year as "YYYY-YY" string; rename temp
    # column to match for the merge, then drop after price columns attach.
    prices_renamed = prices.rename(columns={"obligation_year": "_oy_label"})
    df = df.merge(prices_renamed, on="_oy_label", how="left")

    # Zero-fill null price columns so downstream arithmetic is safe. Nullable
    # mutualisation is preserved as NaN → null on the final row (D-11).
    # Column names match roc-prices.csv header verbatim (D-03):
    #   eroc_gbp_per_roc       — e-ROC clearing price per ROC (nullable)
    #   mutualisation_gbp_total — total GBP mutualisation (not per-ROC); D-11 SY20 only
    for col in ["buyout_gbp_per_roc", "recycle_gbp_per_roc"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)
    if "eroc_gbp_per_roc" not in df.columns:
        df["eroc_gbp_per_roc"] = pd.Series([pd.NA] * len(df), dtype="Float64")
    if "mutualisation_gbp_total" not in df.columns:
        df["mutualisation_gbp_total"] = pd.Series(
            [pd.NA] * len(df), dtype="Float64"
        )

    # --------------------------------------------------------------
    # 8. Compute cost columns (D-02, D-05, D-11).
    # --------------------------------------------------------------
    # mutualisation_gbp_total is the TOTAL GBP amount for the obligation year (D-11),
    # not a per-ROC figure. For a given station×month row we apportion it proportionally
    # as: station_mutualisation = (station_rocs / total_oy_rocs) * total_mutualisation.
    # However, since cost_model.py builds a per-row view, use the total directly as
    # the denominator-free additive term per obligation year (spread across all rows
    # in the rollup). For per-station-month precision: store the raw total in
    # mutualisation_gbp so aggregation.py can roll up correctly without double-counting.
    # The ro_cost_gbp formula adds the full total only once by relying on the
    # aggregation layer to sum across all station-month rows in the OY.
    #
    # Per-station per-ROC contribution: buyout + recycle (D-02 primary, no carbon D-05).
    rocs = df["rocs_issued"].fillna(0.0).astype(float)
    buyout = df["buyout_gbp_per_roc"].astype(float)
    recycle = df["recycle_gbp_per_roc"].astype(float)

    df["ro_cost_gbp"] = rocs * (buyout + recycle)
    # eROC sensitivity: if clearing price absent for an OY, fall back to
    # (buyout + recycle) so the sensitivity column is always populated.
    eroc = df["eroc_gbp_per_roc"].astype(float).fillna(buyout + recycle)
    df["ro_cost_gbp_eroc"] = rocs * eroc
    # RO carries no embedded carbon component (ROC price is legislatively fixed,
    # buyout + recycle). Column kept for schema parity per D-05 docstring above.
    df["ro_cost_gbp_nocarbon"] = df["ro_cost_gbp"]
    # Per-row mutualisation £ total — null iff no mutualisation for that OY.
    # Stored as the raw total (not per-station); aggregation.py picks the first
    # non-null value per OY (all rows in same OY carry identical total).
    df["mutualisation_gbp"] = df["mutualisation_gbp_total"].astype("Float64")

    # --------------------------------------------------------------
    # 9. Gas counterfactual — annual-average lookup by calendar year.
    # --------------------------------------------------------------
    if empty:
        df["gas_counterfactual_gbp"] = pd.Series([], dtype="float64")
        df["premium_gbp"] = pd.Series([], dtype="float64")
    else:
        annual_cf = _annual_counterfactual_gbp_per_mwh()
        cy = df["month_end"].dt.year.astype("int64")
        cf_per_mwh = cy.map(annual_cf).fillna(0.0).astype(float)
        df["gas_counterfactual_gbp"] = cf_per_mwh * df["generation_mwh"].astype(float)
        df["premium_gbp"] = df["ro_cost_gbp"] - df["gas_counterfactual_gbp"]

    # --------------------------------------------------------------
    # 10. Methodology version provenance stamp (D-12 / GOV-02).
    # --------------------------------------------------------------
    df["methodology_version"] = METHODOLOGY_VERSION

    # --------------------------------------------------------------
    # 11. Drop internal columns + order + sort + validate + write.
    # --------------------------------------------------------------
    columns = list(RoStationMonthRow.model_fields.keys())
    # Ensure every expected column is present (empty-frame defence).
    for col in columns:
        if col not in df.columns:
            df[col] = pd.Series([pd.NA] * len(df))
    df = (
        df[columns]
        .sort_values(["station_id", "month_end"], kind="mergesort")
        .reset_index(drop=True)
    )
    df = station_month_schema.validate(df)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_parquet(df, output_dir / "station_month.parquet")
    emit_schema_json(RoStationMonthRow, output_dir / "station_month.schema.json")
    return df
