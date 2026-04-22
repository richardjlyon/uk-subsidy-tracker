"""Forward-projection grain: one row per station with remaining-obligation stats.

Hoisted from plotting/subsidy/remaining_obligations.py::main (lines 80-124).
Preserves the `CFD_ID` → `CfD_ID` rename (portfolio uses uppercase, gen uses
mixed case) and the 15-year vs 35-year (nuclear) contract-length rule.

Determinism discipline (D-21, Pitfall 1):
- Uses a pinned `CURRENT_YEAR` constant derived from the latest settlement
  date in the raw data (NOT `pd.Timestamp.now().year`) — this preserves
  content-identity across rebuilds regardless of wall-clock time.
- Every groupby passes sort=True explicitly.
- Column order = ForwardProjectionRow field declaration order (D-10).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from uk_subsidy_tracker.counterfactual import METHODOLOGY_VERSION
from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.schemas.cfd import ForwardProjectionRow, emit_schema_json
from uk_subsidy_tracker.schemes.cfd.cost_model import _write_parquet


def build_forward_projection(output_dir: Path) -> pd.DataFrame:
    """Build and persist `forward_projection.parquet` (one row per station).

    Columns (per ForwardProjectionRow field order): station_id, technology,
    contract_start_year, contract_end_year, avg_annual_generation_mwh,
    avg_strike_gbp_per_mwh, remaining_committed_mwh, methodology_version.

    `contract_end_year` uses 35 years for nuclear, 15 years for all other
    technologies (the standard pre-AR7 CfD term). This mirrors the chart
    file's rule verbatim — change both in sync if the rule evolves.

    `remaining_committed_mwh` is computed against the **max settlement
    date in the raw data**, not today's date. Rationale: any use of
    `pd.Timestamp.now()` breaks content-identity across rebuilds under
    D-21 (the determinism test rebuilds twice and demands byte-level
    content equality). The max-settlement-date anchor makes the grain a
    pure function of raw input.
    """
    gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    cap = load_lccc_dataset("CfD Contract Portfolio Status")
    cap = cap.rename(columns={"CFD_ID": "CfD_ID"})

    first_gen = (
        gen.groupby("CfD_ID", sort=True)["Settlement_Date"]
        .min()
        .rename("first_gen_date")
    )
    units = cap.merge(first_gen, on="CfD_ID", how="left")

    units["start"] = units["Expected_Start_Date"].fillna(units["first_gen_date"])
    units["contract_years"] = units["Technology_Type"].apply(
        lambda t: 35 if "Nuclear" in str(t) else 15
    )
    units["contract_start_year"] = units["start"].dt.year.astype("Int64")
    units["contract_end_year"] = (
        units["contract_start_year"] + units["contract_years"]
    ).astype("Int64")

    gen_year = gen.copy()
    gen_year["year"] = gen_year["Settlement_Date"].dt.year
    n_years_per_unit = gen_year.groupby("CfD_ID", sort=True)["year"].nunique()

    annual_gen = (
        gen_year.groupby("CfD_ID", sort=True)["CFD_Generation_MWh"]
        .sum()
        .div(n_years_per_unit)
        .rename("avg_annual_generation_mwh")
    )

    strike = (
        gen.groupby("CfD_ID", sort=True)
        .apply(
            lambda g: (
                np.average(
                    g["Strike_Price_GBP_Per_MWh"].dropna(),
                    weights=g.loc[
                        g["Strike_Price_GBP_Per_MWh"].notna(), "CFD_Generation_MWh"
                    ],
                )
                if g["CFD_Generation_MWh"].sum() > 0
                else np.nan
            ),
            include_groups=False,
        )
        .rename("avg_strike_gbp_per_mwh")
    )

    units = units.merge(annual_gen, on="CfD_ID", how="left")
    units = units.merge(strike, on="CfD_ID", how="left")

    # Deterministic "current year" anchor: latest settlement date in the
    # raw data rounded to year. D-21: pure function of raw content.
    current_year_anchor = int(gen["Settlement_Date"].max().year)

    # Drop units we cannot project meaningfully.
    units = units.dropna(
        subset=[
            "contract_end_year",
            "contract_start_year",
            "avg_annual_generation_mwh",
            "avg_strike_gbp_per_mwh",
        ]
    )

    units["remaining_years"] = (
        units["contract_end_year"].astype(int) - current_year_anchor
    ).clip(lower=0)
    units["remaining_committed_mwh"] = (
        units["avg_annual_generation_mwh"] * units["remaining_years"]
    )

    units = units.rename(
        columns={
            "CfD_ID": "station_id",
            "Technology_Type": "technology",
        }
    )
    units["methodology_version"] = METHODOLOGY_VERSION
    units["contract_start_year"] = units["contract_start_year"].astype(int)
    units["contract_end_year"] = units["contract_end_year"].astype(int)

    columns = list(ForwardProjectionRow.model_fields.keys())
    df = (
        units[columns]
        .sort_values("station_id", kind="mergesort")
        .reset_index(drop=True)
    )

    _write_parquet(df, output_dir / "forward_projection.parquet")
    emit_schema_json(
        ForwardProjectionRow, output_dir / "forward_projection.schema.json"
    )
    return df
