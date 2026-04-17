"""Capture-price ratio and its cost consequence — the cannibalisation effect.

Two-panel chart:
- Top: capture-price ratio falling — wind generators sell into
  increasingly cheap hours as more capacity is built.
- Bottom: average CfD levy payment per MWh rising — the direct
  consequence. As market price falls below strike price, consumers
  pay a bigger top-up per MWh.

The two lines mirror each other: one goes down, the other goes up.
That's the cannibalisation story.

Sources: LCCC "Actual CfD Generation and avoided GHG emissions".
Methodology:
- Capture price = generation-weighted average Market Reference Price
  per technology per year.
- Time-weighted price = daily average MRP, then averaged across days.
- Capture ratio = capture price / time-weighted price × 100%.
- Levy per MWh = generation-weighted average of
  (Strike_Price - Market_Reference_Price) per technology per year.
  This is the actual subsidy cost per unit of wind electricity.
Caveats:
- Market Reference Price is per CfD unit, not the whole wholesale
  market. The time-weighted average is a proxy.
- Only years with meaningful generation per technology are shown.
- Current incomplete year excluded.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart

TECH_CONFIG = {
    "Offshore Wind": {"color": "#1f77b4"},
    "Onshore Wind": {"color": "#6baed6"},
}

MIN_ANNUAL_GEN_MWH = 10_000


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df = df.dropna(
        subset=[
            "Market_Reference_Price_GBP_Per_MWh",
            "Strike_Price_GBP_Per_MWh",
            "CFD_Generation_MWh",
        ]
    )
    df = df[df["CFD_Generation_MWh"] > 0]
    df["year"] = df["Settlement_Date"].dt.year

    current_year = pd.Timestamp.now().year
    df = df[df["year"] < current_year]

    daily_avg = df.groupby("Settlement_Date")["Market_Reference_Price_GBP_Per_MWh"].mean()
    yearly_tw = daily_avg.groupby(daily_avg.index.year).mean()

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Capture-price ratio — wind sells into cheaper hours",
            "Consequence — AR1 levy per MWh rises (same contracts, same strike prices)",
        ],
        vertical_spacing=0.10,
    )

    for tech, cfg in TECH_CONFIG.items():
        tech_df = df[df["Technology"] == tech]

        years = []
        ratios = []
        levy_per_mwh = []

        for year in sorted(tech_df["year"].unique()):
            yr = tech_df[tech_df["year"] == year]
            if yr["CFD_Generation_MWh"].sum() < MIN_ANNUAL_GEN_MWH:
                continue
            if year not in yearly_tw.index:
                continue

            capture = np.average(
                yr["Market_Reference_Price_GBP_Per_MWh"],
                weights=yr["CFD_Generation_MWh"],
            )
            ratio = capture / yearly_tw[year] * 100

            levy = np.average(
                yr["Strike_Price_GBP_Per_MWh"] - yr["Market_Reference_Price_GBP_Per_MWh"],
                weights=yr["CFD_Generation_MWh"],
            )

            years.append(year)
            ratios.append(ratio)
            levy_per_mwh.append(levy)

        fig.add_trace(
            go.Scatter(
                x=years,
                y=ratios,
                name=tech,
                mode="lines+markers",
                line={"color": cfg["color"], "width": 2.5},
                marker={"size": 8},
                hovertemplate=f"{tech}<br>%{{x}}<br>%{{y:.0f}}%<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # Bottom panel: AR1 wind levy per MWh — same contracts, same strike
    # prices, so any change is pure cannibalisation
    ar1 = df[
        (df["Technology"].str.contains("Wind", na=False))
        & (df["Allocation_round"] == "Allocation Round 1")
    ]
    ar1_annual = ar1.groupby("year").agg(
        levy=("CFD_Payments_GBP", "sum"),
        gen=("CFD_Generation_MWh", "sum"),
    )
    ar1_annual = ar1_annual[ar1_annual["gen"] > MIN_ANNUAL_GEN_MWH]
    ar1_annual["levy_per_mwh"] = ar1_annual["levy"] / ar1_annual["gen"]

    bar_colors = [
        "#1f77b4" if v >= 0 else "#2ca02c" for v in ar1_annual["levy_per_mwh"]
    ]
    fig.add_trace(
        go.Bar(
            x=ar1_annual.index.tolist(),
            y=ar1_annual["levy_per_mwh"].tolist(),
            name="AR1 wind levy per MWh",
            marker_color=bar_colors,
            hovertemplate="%{x}<br>£%{y:.0f}/MWh<extra></extra>",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.add_hline(
        y=100,
        line_dash="dash",
        line_color="grey",
        line_width=1.5,
        annotation_text="100% = captures average market price",
        annotation_position="bottom right",
        annotation_font_size=10,
        row=1,
        col=1,
    )

    fig.update_yaxes(title="Capture-price ratio", ticksuffix="%", row=1, col=1)
    fig.update_yaxes(
        title="AR1 wind levy (£/MWh)",
        tickprefix="£",
        ticksuffix="/MWh",
        row=2,
        col=1,
    )
    fig.update_xaxes(dtick=1)
    fig.update_layout(
        title="The Cannibalisation Effect — wind crashes its own price, consumers pay more",
        height=800,
        hovermode="x unified",
    )

    save_chart(fig, "cannibalisation_capture_ratio")


if __name__ == "__main__":
    main()
