"""Daily capacity factor heatmaps — year × day-of-year.

Separate heatmaps for wind and solar, each normalised to its own
installed CfD capacity. Blue (low) to red (high) colour scale.
Dunkelflaute weeks show up as cold blue stripes in the wind panel;
solar's winter collapse is even starker.

Sources: LCCC "Actual CfD Generation" and "CfD Contract Portfolio Status".
Methodology:
- Daily CF = sum(generation_MWh) / (installed_capacity_MW × 24 hours).
- Installed capacity on each date is derived by summing the contract
  capacity of all units whose first generation date is on or before
  that date. Contract capacity is fixed per unit (does not change over
  time), so the denominator grows only as new units commission.
- Wind and solar are plotted separately to avoid the mix effect: the
  fleet's solar share grows over time, and blending would make later
  years appear colder simply because solar has lower CF than wind.
- Both panels share the same 0–100% colour scale for comparability.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart

COLORSCALE = [
    [0.0, "#08306b"],
    [0.15, "#2171b5"],
    [0.3, "#6baed6"],
    [0.45, "#bdd7e7"],
    [0.55, "#fcae91"],
    [0.7, "#fb6a4a"],
    [0.85, "#cb181d"],
    [1.0, "#67000d"],
]

TECH_GROUPS = {
    "Wind": ["Offshore Wind", "Onshore Wind"],
    "Solar": ["Solar PV"],
}


def _compute_daily_cf(
    df: pd.DataFrame,
    df_cap: pd.DataFrame,
    tech_types: list[str],
) -> pd.DataFrame:
    cap = df_cap[df_cap["Technology_Type"].isin(tech_types)]
    unit_cap = cap.groupby("CfD_ID")["Maximum_Contract_Capacity_MW"].sum()

    gen = df[df["Technology"].isin(
        df[df["CfD_ID"].isin(unit_cap.index)]["Technology"].unique()
    )]
    gen = gen[gen["CfD_ID"].isin(unit_cap.index)]

    first_gen = gen.groupby("CfD_ID")["Settlement_Date"].min().rename("start_date")
    unit_info = pd.concat([first_gen, unit_cap], axis=1).dropna()

    all_dates = pd.date_range(gen["Settlement_Date"].min(), gen["Settlement_Date"].max())

    cap_by_date = np.zeros(len(all_dates))
    for _, row in unit_info.iterrows():
        mask = all_dates >= row["start_date"]
        cap_by_date[mask] += row["Maximum_Contract_Capacity_MW"]
    installed = pd.Series(cap_by_date, index=all_dates)

    daily_gen = gen.groupby("Settlement_Date")["CFD_Generation_MWh"].sum()

    result = daily_gen.reset_index()
    result["capacity_mw"] = result["Settlement_Date"].map(installed)
    result["capacity_factor"] = result["CFD_Generation_MWh"] / (
        result["capacity_mw"] * 24
    )
    result["year"] = result["Settlement_Date"].dt.year
    result["day_of_year"] = result["Settlement_Date"].dt.dayofyear
    return result


def _build_grid(daily_df: pd.DataFrame, years: list[int]) -> np.ndarray:
    max_day = 366
    grid = np.full((len(years), max_day), np.nan)
    for i, year in enumerate(years):
        year_data = daily_df[daily_df["year"] == year]
        for _, row in year_data.iterrows():
            grid[i, int(row["day_of_year"]) - 1] = row["capacity_factor"]
    return grid


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df_cap = load_lccc_dataset("CfD Contract Portfolio Status")
    df_cap = df_cap.rename(columns={"CFD_ID": "CfD_ID"})

    month_starts = [pd.Timestamp(2024, m, 1).dayofyear for m in range(1, 13)]
    month_labels = [pd.Timestamp(2024, m, 1).strftime("%b") for m in range(1, 13)]

    panels = list(TECH_GROUPS.keys())
    fig = make_subplots(
        rows=len(panels),
        cols=1,
        shared_xaxes=True,
        subplot_titles=[f"{name} — Daily Capacity Factor" for name in panels],
        vertical_spacing=0.08,
    )

    for row_idx, (name, tech_types) in enumerate(TECH_GROUPS.items(), start=1):
        daily_df = _compute_daily_cf(df, df_cap, tech_types)
        years = sorted(daily_df["year"].unique())
        grid = _build_grid(daily_df, years)

        fig.add_trace(
            go.Heatmap(
                z=grid,
                x=list(range(1, 367)),
                y=[str(y) for y in years],
                colorscale=COLORSCALE,
                colorbar={
                    "title": "CF",
                    "tickformat": ".0%",
                    "len": 0.4,
                    "y": 1.0 - (row_idx - 0.5) / len(panels),
                },
                hovertemplate=f"{name}<br>Day %{{x}}, %{{y}}<br>CF: %{{z:.1%}}<extra></extra>",
                zmin=0,
                zmax=1,
            ),
            row=row_idx,
            col=1,
        )

    for row_idx in range(1, len(panels) + 1):
        fig.update_xaxes(
            tickvals=month_starts,
            ticktext=month_labels,
            row=row_idx,
            col=1,
        )
        fig.update_yaxes(autorange="reversed", row=row_idx, col=1)

    fig.update_layout(
        title="CfD Fleet Daily Capacity Factor — Wind Stripes",
        height=800,
    )

    save_chart(fig, "intermittency_generation_heatmap")


if __name__ == "__main__":
    main()
