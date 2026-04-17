"""Shared data preparation for capacity factor plots.

Sources: LCCC "Actual CfD Generation" (generation MWh per unit per day)
joined to "CfD Contract Portfolio Status" (installed capacity MW per unit)
on CfD_ID. Join is inner — only units present in both datasets.

Methodology:
- CF = generation_MWh / (capacity_MW × hours_in_month)
- The current incomplete month is excluded to avoid partial-month bias.
- aggregate_by_technology() uses capacity-weighted sums (not averages of
  per-unit CFs) to avoid the "average of averages" distortion where small
  units would count equally with large ones.
"""

import pandas as pd

from cfd_payment.data import load_lccc_dataset

WIND_AND_SOLAR = ["Solar PV", "Onshore Wind", "Offshore Wind"]


def prepare_capacity_data(
    technologies: list[str] | None = None,
) -> pd.DataFrame:
    """Load, merge, and compute per-unit monthly capacity factor.

    Returns a DataFrame with columns:
        CfD_ID, month, hours_in_month, generation_MWh,
        Technology_Type, Maximum_Contract_Capacity_MW, capacity_factor
    """
    df_gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df_cap = load_lccc_dataset("CfD Contract Portfolio Status")

    capacity = df_cap[
        ["CFD_ID", "Technology_Type", "Maximum_Contract_Capacity_MW"]
    ].rename(columns={"CFD_ID": "CfD_ID"})

    df_gen["month"] = df_gen["Settlement_Date"].dt.to_period("M")
    current_month = pd.Timestamp.now().to_period("M")
    df_gen = df_gen[df_gen["month"] < current_month]
    df_gen["hours_in_month"] = df_gen["month"].dt.days_in_month * 24

    monthly_gen = (
        df_gen.groupby(["CfD_ID", "Name_of_CfD_Unit", "month", "hours_in_month"])
        .agg(generation_MWh=("CFD_Generation_MWh", "sum"))
        .reset_index()
    )

    merged = monthly_gen.merge(capacity, on="CfD_ID", how="inner")

    if technologies:
        merged = merged[merged["Technology_Type"].isin(technologies)]

    merged["capacity_factor"] = merged["generation_MWh"] / (
        merged["Maximum_Contract_Capacity_MW"] * merged["hours_in_month"]
    )

    return merged


def aggregate_by_technology(
    merged: pd.DataFrame,
    groupby_cols: list[str],
) -> pd.DataFrame:
    """Capacity-weighted aggregation of CF by technology and given time columns.

    Avoids the 'average of averages' trap by summing generation and
    theoretical maximum separately, then dividing.
    """
    merged = merged.copy()
    merged["capacity_hours"] = (
        merged["Maximum_Contract_Capacity_MW"] * merged["hours_in_month"]
    )

    by_tech = (
        merged.groupby(["Technology_Type"] + groupby_cols)
        .agg(
            total_gen=("generation_MWh", "sum"),
            total_capacity_hours=("capacity_hours", "sum"),
        )
        .reset_index()
    )
    by_tech["capacity_factor"] = by_tech["total_gen"] / by_tech["total_capacity_hours"]
    return by_tech
