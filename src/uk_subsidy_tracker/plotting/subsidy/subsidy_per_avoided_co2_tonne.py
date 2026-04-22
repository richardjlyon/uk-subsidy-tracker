"""CfD subsidy cost per tonne of CO2 avoided.

Two-panel chart:
- Top: £/tCO2 avoided by allocation round (IC and AR1/AR2 only — later
  rounds have too little generation to be meaningful).
- Bottom: CO2 avoided per MWh over time — showing the diminishing returns
  as the grid gets cleaner.

The key insight: as more renewables are added, each new MWh displaces
less CO2 (because it's displacing other clean generation, not gas). So
the subsidy cost per tonne avoided is *accelerating upward* — the more
we spend, the less carbon we avoid per pound.

Sources: LCCC "Actual CfD Generation and avoided GHG emissions".
Methodology:
- £/tCO2 = sum(CFD_Payments_GBP) / sum(Avoided_GHG_tonnes_CO2e) per
  allocation round per year.
- CO2 avoided per MWh = sum(Avoided_GHG_tonnes_CO2e) / sum(CFD_Generation_MWh)
  — this is determined by grid carbon intensity, not the CfD generator.
- 2022 excluded: negative payments (clawback) produce meaningless negative
  £/tCO2 that distorts the chart.
- Rounds with <1 TWh total generation excluded (AR4, AR5, AR6).
- Reference lines: DEFRA social cost of carbon (~£280/t) and UK ETS
  price (~£50/t) — if the subsidy costs more than these, we're paying
  more to avoid carbon via CfDs than the government says carbon is worth.
"""

import pandas as pd
import plotly.graph_objects as go

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import ChartBuilder

ROUNDS_TO_SHOW = ["Investment Contract", "Allocation Round 1", "Allocation Round 2"]
ROUND_COLORS = {
    "Investment Contract": "#d62728",
    "Allocation Round 1": "#1f77b4",
    "Allocation Round 2": "#2ca02c",
}


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df["Year"] = df["Settlement_Date"].dt.year

    df = df[df["Year"].between(2017, 2025) & (df["Year"] != 2022)]

    grouped = (
        df.groupby(["Allocation_round", "Year"])
        .agg(
            payments=("CFD_Payments_GBP", "sum"),
            co2_avoided=("Avoided_GHG_tonnes_CO2e", "sum"),
            generation=("CFD_Generation_MWh", "sum"),
        )
        .reset_index()
    )
    grouped["cost_per_tonne"] = grouped["payments"] / grouped["co2_avoided"]
    grouped["co2_per_mwh"] = grouped["co2_avoided"] / grouped["generation"]

    fleet = (
        df.groupby("Year")
        .agg(
            co2_avoided=("Avoided_GHG_tonnes_CO2e", "sum"),
            generation=("CFD_Generation_MWh", "sum"),
        )
        .reset_index()
    )
    fleet["co2_per_mwh"] = fleet["co2_avoided"] / fleet["generation"]

    builder = ChartBuilder(
        title="CfD Subsidy Cost per Tonne of CO₂ Avoided — rising as the grid gets cleaner",
        height=800,
    )
    fig = builder.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Subsidy cost per tonne of CO₂ avoided",
            "CO₂ avoided per MWh — diminishing as the grid gets cleaner",
        ],
        vertical_spacing=0.10,
    )

    # --- Top panel: £/tCO2 by round ---
    for ar in ROUNDS_TO_SHOW:
        ar_data = grouped[grouped["Allocation_round"] == ar]
        if ar_data.empty:
            continue
        fig.add_trace(
            go.Scatter(
                x=ar_data["Year"],
                y=ar_data["cost_per_tonne"],
                name=ar,
                mode="lines+markers",
                line={"color": ROUND_COLORS[ar], "width": 2.5},
                marker={"size": 7},
                hovertemplate=f"{ar}<br>%{{x}}<br>£%{{y:.0f}}/tCO₂<extra></extra>",
            ),
            row=1,
            col=1,
        )

    fig.add_hline(
        y=280,
        line_dash="dash",
        line_color="red",
        line_width=1.5,
        annotation_text="DEFRA social cost of carbon (~£280/t)",
        annotation_position="bottom right",
        annotation_font_size=10,
        row=1,
        col=1,
    )
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="grey",
        line_width=1.5,
        annotation_text="UK ETS price (~£50/t)",
        annotation_position="bottom right",
        annotation_font_size=10,
        row=1,
        col=1,
    )

    # --- Bottom panel: CO2 per MWh ---
    fig.add_trace(
        go.Scatter(
            x=fleet["Year"],
            y=fleet["co2_per_mwh"],
            name="Fleet CO₂ avoided per MWh",
            mode="lines+markers",
            line={"color": "#666666", "width": 2.5},
            marker={"size": 7},
            hovertemplate="%{x}<br>%{y:.3f} tCO₂/MWh<extra></extra>",
        ),
        row=2,
        col=1,
    )

    builder.format_currency_axis(
        fig,
        axis="y",
        suffix="",
        title="£ per tonne CO₂ avoided",
        row=1,
        col=1,
    )
    fig.update_yaxes(rangemode="tozero", row=1, col=1)
    fig.update_yaxes(
        title="tCO₂ per MWh",
        rangemode="tozero",
        row=2,
        col=1,
    )
    fig.update_xaxes(dtick=1, row=1, col=1)
    fig.update_xaxes(dtick=1, row=2, col=1)
    fig.update_layout(
        hovermode="x unified",
    )

    builder.save(fig, "subsidy_cost_per_avoided_co2_tonne", export_twitter=True)


if __name__ == "__main__":
    main()
