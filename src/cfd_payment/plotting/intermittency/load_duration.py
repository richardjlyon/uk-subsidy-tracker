"""Load-duration curves for CfD wind and solar fleets (capacity factor).

Separate curves for wind and solar, each normalised to its own installed
capacity. Shows what fraction of the time each fleet runs above a given CF.

Sources: LCCC "Actual CfD Generation" and "CfD Contract Portfolio Status".
Methodology:
- Daily CF = sum(generation_MWh) / (installed_capacity_MW × 24 hours).
- Installed capacity on each date is the sum of contract capacity for all
  units whose first generation date is on or before that date (same approach
  as the generation heatmap).
- Days are sorted from highest to lowest CF.
- X-axis is raw day count; threshold annotations include annualised equiv.
- Wind and solar plotted separately to avoid the mix effect — blending would
  drag the curve down as the solar share of installed capacity grows.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart

TECH_GROUPS = {
    "Wind": {
        "types": ["Offshore Wind", "Onshore Wind"],
        "color": "#1f77b4",
        "thresholds": [(0.6, "60%"), (0.4, "40%"), (0.2, "20%"), (0.05, "5%")],
    },
    "Solar": {
        "types": ["Solar PV"],
        "color": "#ff7f0e",
        "thresholds": [(0.3, "30%"), (0.2, "20%"), (0.1, "10%"), (0.02, "2%")],
    },
}


def _installed_capacity_by_date(
    df: pd.DataFrame,
    df_cap: pd.DataFrame,
    tech_types: list[str],
) -> pd.Series:
    cap = df_cap[df_cap["Technology_Type"].isin(tech_types)]
    unit_cap = cap.groupby("CfD_ID")["Maximum_Contract_Capacity_MW"].sum()

    gen = df[df["CfD_ID"].isin(unit_cap.index)]
    first_gen = gen.groupby("CfD_ID")["Settlement_Date"].min().rename("start_date")
    unit_info = pd.concat([first_gen, unit_cap], axis=1).dropna()

    all_dates = pd.date_range(gen["Settlement_Date"].min(), gen["Settlement_Date"].max())
    cap_by_date = np.zeros(len(all_dates))
    for _, row in unit_info.iterrows():
        mask = all_dates >= row["start_date"]
        cap_by_date[mask] += row["Maximum_Contract_Capacity_MW"]
    return pd.Series(cap_by_date, index=all_dates)


def _compute_daily_cf(
    df: pd.DataFrame,
    df_cap: pd.DataFrame,
    tech_types: list[str],
) -> np.ndarray:
    gen = df[df["CfD_ID"].isin(
        df_cap[df_cap["Technology_Type"].isin(tech_types)]["CfD_ID"]
    )]
    daily_gen = gen.groupby("Settlement_Date")["CFD_Generation_MWh"].sum()

    installed = _installed_capacity_by_date(df, df_cap, tech_types)

    daily_df = daily_gen.reset_index()
    daily_df["capacity_mw"] = daily_df["Settlement_Date"].map(installed)
    daily_df["cf"] = daily_df["CFD_Generation_MWh"] / (daily_df["capacity_mw"] * 24)
    return daily_df["cf"].sort_values(ascending=False).values


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df_cap = load_lccc_dataset("CfD Contract Portfolio Status")
    df_cap = df_cap.rename(columns={"CFD_ID": "CfD_ID"})

    panels = list(TECH_GROUPS.keys())
    fig = make_subplots(
        rows=1,
        cols=len(panels),
        shared_yaxes=True,
        subplot_titles=[f"{name} — Load-Duration Curve" for name in panels],
    )

    for col_idx, (name, cfg) in enumerate(TECH_GROUPS.items(), start=1):
        sorted_cf = _compute_daily_cf(df, df_cap, cfg["types"])
        n_days = len(sorted_cf)
        day_rank = np.arange(1, n_days + 1)
        mean_cf = sorted_cf.mean()
        n_years = n_days / 365.25

        fig.add_trace(
            go.Scatter(
                x=day_rank,
                y=sorted_cf,
                mode="lines",
                line={"color": cfg["color"], "width": 2},
                fill="tozeroy",
                fillcolor=cfg["color"].replace(")", ",0.15)").replace("rgb", "rgba")
                if "rgb" in cfg["color"]
                else f"rgba({int(cfg['color'][1:3],16)},{int(cfg['color'][3:5],16)},{int(cfg['color'][5:7],16)},0.15)",
                hovertemplate=f"{name}<br>Day %{{x}}<br>CF: %{{y:.1%}}<extra></extra>",
                showlegend=False,
            ),
            row=1,
            col=col_idx,
        )

        fig.add_hline(
            y=mean_cf,
            line_dash="dash",
            line_color="black",
            line_width=1.5,
            annotation_text=f"Mean ({mean_cf:.0%})",
            annotation_position="top right",
            annotation_font_size=10,
            row=1,
            col=col_idx,
        )

        for threshold, label in cfg["thresholds"]:
            days_above = int((sorted_cf >= threshold).sum())
            days_per_year = days_above / n_years
            fig.add_trace(
                go.Scatter(
                    x=[days_above],
                    y=[threshold],
                    mode="markers+text",
                    marker={"size": 7, "color": "red"},
                    text=[f">{label}: {days_above}d (≈{days_per_year:.0f}/yr)"],
                    textposition="middle right",
                    textfont={"size": 9},
                    showlegend=False,
                    hovertemplate=f">{label} CF<br>{days_above} days<br>≈{days_per_year:.0f}/yr<extra></extra>",
                ),
                row=1,
                col=col_idx,
            )

    fig.update_yaxes(title="Daily Capacity Factor", tickformat=".0%", col=1)
    fig.update_yaxes(tickformat=".0%", col=2)
    fig.update_xaxes(title="Days (best → worst)")
    fig.update_layout(
        title="CfD Load-Duration Curves — Wind and Solar daily capacity factor",
        height=600,
    )

    save_chart(fig, "intermittency_load_duration")


if __name__ == "__main__":
    main()
