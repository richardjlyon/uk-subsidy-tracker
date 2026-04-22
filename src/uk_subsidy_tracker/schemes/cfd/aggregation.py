"""Annual + per-technology + per-allocation-round rollups of station_month.

Three builders: build_annual_summary, build_by_technology,
build_by_allocation_round. Each reads `station_month.parquet` from the
same output_dir written by build_station_month (D-03: the station × month
derivation is canonical; every rollup is a groupby-sum of it, guaranteeing
exact row-conservation under pd.testing.assert_series_equal).

Determinism discipline (D-21, Pitfall 1):
- Reads the already-written `station_month.parquet` rather than re-reading
  raw CSV — guarantees rollup consistency with the upstream grain and
  isolates each builder from CSV-parse nondeterminism risk.
- Every groupby passes sort=True explicitly.
- Counterfactual join uses the compute_counterfactual() pure function.

The counterfactual_payments_gbp column on annual_summary comes from a
separate counterfactual computation joined at the month_end anchor —
this is the derived quantity Plan 06 will use to activate the
premium-over-gas headline numbers.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from uk_subsidy_tracker.counterfactual import (
    METHODOLOGY_VERSION,
    compute_counterfactual,
)
from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.schemas.cfd import (
    AnnualSummaryRow,
    ByAllocationRoundRow,
    ByTechnologyRow,
    emit_schema_json,
)
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet


def _read_station_month(output_dir: Path) -> pd.DataFrame:
    """Load the canonical station × month grain from the current rebuild."""
    path = output_dir / "station_month.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — call build_station_month(output_dir) first."
        )
    return pq.read_table(path).to_pandas()


def build_annual_summary(output_dir: Path) -> pd.DataFrame:
    """Build and persist `annual_summary.parquet` (one row per calendar year).

    Columns (per AnnualSummaryRow field order): year, cfd_generation_mwh,
    cfd_payments_gbp, counterfactual_payments_gbp, premium_over_gas_gbp,
    methodology_version.

    counterfactual_payments_gbp is sum(counterfactual_total × CFD_Generation_MWh)
    per year, using the daily gas counterfactual joined to actuals at
    Settlement_Date. Re-uses load_lccc_dataset + compute_counterfactual
    rather than station_month for this column because counterfactual needs
    daily resolution for accurate price × volume; station_month.parquet
    has already collapsed to monthly.
    """
    sm = _read_station_month(output_dir)
    # Cast to int64 to match AnnualSummaryRow.year declared dtype (D-10).
    sm["year"] = sm["month_end"].dt.year.astype("int64")

    annual_cfd = (
        sm.groupby("year", sort=True)
        .agg(
            cfd_generation_mwh=("cfd_generation_mwh", "sum"),
            cfd_payments_gbp=("cfd_payments_gbp", "sum"),
        )
        .reset_index()
    )

    # Counterfactual: daily gas-alternative £/MWh × daily CfD generation.
    gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    gen = gen.dropna(subset=["CFD_Generation_MWh", "Strike_Price_GBP_Per_MWh"])
    gen = gen[gen["CFD_Generation_MWh"] > 0]
    daily_gen = (
        gen.groupby("Settlement_Date", sort=True)["CFD_Generation_MWh"]
        .sum()
        .rename("gen_mwh")
    )
    cf_daily = compute_counterfactual().set_index("date")["counterfactual_total"]
    daily = pd.concat([daily_gen, cf_daily.reindex(daily_gen.index)], axis=1)
    daily = daily.dropna(subset=["counterfactual_total"])
    daily["cf_gbp"] = daily["counterfactual_total"] * daily["gen_mwh"]
    # daily_gen was grouped on Settlement_Date; the index name survives concat.
    daily["year"] = daily.index.year.astype("int64")
    annual_cf = (
        daily.groupby("year", sort=True)["cf_gbp"]
        .sum()
        .rename("counterfactual_payments_gbp")
        .reset_index()
    )

    df = annual_cfd.merge(annual_cf, on="year", how="left")
    df["counterfactual_payments_gbp"] = df["counterfactual_payments_gbp"].fillna(0.0)
    df["premium_over_gas_gbp"] = (
        df["cfd_payments_gbp"] - df["counterfactual_payments_gbp"]
    )
    df["methodology_version"] = METHODOLOGY_VERSION

    # Column order = AnnualSummaryRow field order (D-10).
    columns = list(AnnualSummaryRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values("year", kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "annual_summary.parquet")
    emit_schema_json(AnnualSummaryRow, output_dir / "annual_summary.schema.json")
    return df


def build_by_technology(output_dir: Path) -> pd.DataFrame:
    """Build and persist `by_technology.parquet` (year × technology grain)."""
    sm = _read_station_month(output_dir)
    # Cast to int64 to match ByTechnologyRow.year declared dtype (D-10).
    sm["year"] = sm["month_end"].dt.year.astype("int64")

    df = (
        sm.groupby(["year", "technology"], sort=True, dropna=False)
        .agg(
            cfd_generation_mwh=("cfd_generation_mwh", "sum"),
            cfd_payments_gbp=("cfd_payments_gbp", "sum"),
        )
        .reset_index()
    )
    df["methodology_version"] = METHODOLOGY_VERSION

    columns = list(ByTechnologyRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["year", "technology"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "by_technology.parquet")
    emit_schema_json(ByTechnologyRow, output_dir / "by_technology.schema.json")
    return df


def build_by_allocation_round(output_dir: Path) -> pd.DataFrame:
    """Build and persist `by_allocation_round.parquet`.

    One row per (year, allocation_round). avoided_co2_tonnes comes from
    the raw LCCC CSV (Avoided_GHG_tonnes_CO2e) because station_month does
    not carry it. Determinism preserved: identical raw → identical sum.
    """
    sm = _read_station_month(output_dir)
    # Cast to int64 to match ByAllocationRoundRow.year declared dtype (D-10).
    sm["year"] = sm["month_end"].dt.year.astype("int64")

    cfd_roll = (
        sm.groupby(["year", "allocation_round"], sort=True, dropna=False)
        .agg(
            cfd_generation_mwh=("cfd_generation_mwh", "sum"),
            cfd_payments_gbp=("cfd_payments_gbp", "sum"),
        )
        .reset_index()
    )

    # Avoided CO2 comes from the raw LCCC settlement file — the portfolio-
    # derived allocation_round join is already on station_month, but we
    # need the Avoided_GHG_tonnes_CO2e column which station_month drops.
    gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    gen = gen.dropna(subset=["CFD_Generation_MWh", "Strike_Price_GBP_Per_MWh"])
    gen = gen[gen["CFD_Generation_MWh"] > 0]
    gen["year"] = gen["Settlement_Date"].dt.year.astype("int64")
    co2 = (
        gen.groupby(["year", "Allocation_round"], sort=True, dropna=False)[
            "Avoided_GHG_tonnes_CO2e"
        ]
        .sum()
        .rename("avoided_co2_tonnes")
        .reset_index()
        .rename(columns={"Allocation_round": "allocation_round"})
    )

    df = cfd_roll.merge(co2, on=["year", "allocation_round"], how="left")
    df["avoided_co2_tonnes"] = df["avoided_co2_tonnes"].fillna(0.0)
    df["methodology_version"] = METHODOLOGY_VERSION

    columns = list(ByAllocationRoundRow.model_fields.keys())
    df = (
        df[columns]
        .sort_values(["year", "allocation_round"], kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "by_allocation_round.parquet")
    emit_schema_json(
        ByAllocationRoundRow, output_dir / "by_allocation_round.schema.json"
    )
    return df
