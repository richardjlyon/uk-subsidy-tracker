"""Existing CfD contract obligations — annual and cumulative, two scenarios.

Four-panel chart (2×2):
- Top row: annual cost (£bn/yr) still active per year, stacked by round.
- Bottom row: cumulative cost (£bn) over the remaining contract life.
- Left column: flat scenario — current generation levels persist.
- Right column: NESO growth scenario — generation scales with projected
  UK electricity demand growth (~30% by 2035, doubling by 2050).

These are contracts already signed. Future auction rounds (AR7, AR8...)
will add further obligations on top.

Sources: LCCC "Actual CfD Generation" and "CfD Contract Portfolio Status".
NESO demand growth projections (280 TWh 2024 → 390 TWh 2035 → 692 TWh 2050).
Methodology:
- Contract start = Expected_Start_Date from portfolio data; if missing,
  first generation date from actuals is used as proxy.
- Contract length = 15 years for all renewables, 35 years for nuclear.
- Annual cost per unit = strike_price × average_annual_generation_MWh.
  Strike prices are contractually fixed. Generation averaged from
  historical actuals — the best available proxy for future output.
- Growth scenario applies a linear interpolation of NESO's demand
  projections as a multiplier to generation volumes.
- Only Investment Contract, AR1, and AR2 shown — later rounds have
  insufficient generation history to project meaningfully.
- Only units with positive generation included.
Caveats:
- Future costs are estimates — actual generation varies with weather.
- Growth scenario assumes CfD generation scales with total demand,
  which is the government's stated plan but not guaranteed.
- Nuclear (Hinkley) not yet generating so not shown.
- Contract length of 15 years is the standard CfD term. Investment
  Contracts were individually negotiated and their exact terms are
  not publicly confirmed; 15 years is assumed based on the standard.
- From AR7, contract length increases to 20 years for wind and solar,
  making future lock-in even longer — not reflected here as these
  are existing contracts only.
- Drax has a separate new 4-year biomass CfD (2027-2031) which is
  not included; only the original Investment Contract is shown.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import ChartBuilder

ROUND_COLORS = {
    "Investment Contract": "#d62728",
    "Allocation Round 1": "#1f77b4",
    "Allocation Round 2": "#2ca02c",
}

# NESO demand projections (TWh) — used to compute growth multiplier
DEMAND_ANCHORS = {
    2024: 280,
    2035: 390,
    2050: 692,
}


def _demand_multiplier(year: int) -> float:
    """Growth multiplier relative to 2024, linearly interpolated."""
    years = sorted(DEMAND_ANCHORS.keys())
    if year <= years[0]:
        return 1.0
    if year >= years[-1]:
        return DEMAND_ANCHORS[years[-1]] / DEMAND_ANCHORS[years[0]]
    for i in range(len(years) - 1):
        if years[i] <= year <= years[i + 1]:
            frac = (year - years[i]) / (years[i + 1] - years[i])
            twh = DEMAND_ANCHORS[years[i]] + frac * (
                DEMAND_ANCHORS[years[i + 1]] - DEMAND_ANCHORS[years[i]]
            )
            return twh / DEMAND_ANCHORS[years[0]]
    return 1.0


def main() -> None:
    gen = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    cap = load_lccc_dataset("CfD Contract Portfolio Status")
    cap = cap.rename(columns={"CFD_ID": "CfD_ID"})

    first_gen = gen.groupby("CfD_ID")["Settlement_Date"].min().rename("first_gen_date")
    units = cap.merge(first_gen, on="CfD_ID", how="left")

    units["start"] = units["Expected_Start_Date"].fillna(units["first_gen_date"])
    units["contract_years"] = units["Technology_Type"].apply(
        lambda t: 35 if "Nuclear" in str(t) else 15
    )
    units["end_year"] = units["start"].dt.year + units["contract_years"]

    gen["year"] = gen["Settlement_Date"].dt.year
    n_years_per_unit = gen.groupby("CfD_ID")["year"].nunique()

    annual_gen = (
        gen.groupby("CfD_ID")["CFD_Generation_MWh"]
        .sum()
        .div(n_years_per_unit)
        .rename("avg_annual_gen")
    )

    strike = (
        gen.groupby("CfD_ID")
        .apply(
            lambda g: np.average(
                g["Strike_Price_GBP_Per_MWh"].dropna(),
                weights=g.loc[
                    g["Strike_Price_GBP_Per_MWh"].notna(), "CFD_Generation_MWh"
                ],
            )
            if g["CFD_Generation_MWh"].sum() > 0
            else np.nan
        )
        .rename("avg_strike")
    )

    units = units.merge(annual_gen, on="CfD_ID", how="left")
    units = units.merge(strike, on="CfD_ID", how="left")
    units["annual_cost"] = units["avg_strike"] * units["avg_annual_gen"]
    units = units.dropna(subset=["end_year", "annual_cost"])
    units = units[units["annual_cost"] > 0]
    units["end_year"] = units["end_year"].astype(int)

    current_year = pd.Timestamp.now().year
    future = units[units["end_year"] > current_year].copy()
    max_year = int(future["end_year"].max())
    years = list(range(current_year, max_year + 1))

    future["remaining_years"] = future["end_year"] - current_year
    total_flat_bn = (future["annual_cost"] * future["remaining_years"]).sum() / 1e9
    total_growth_bn = (
        sum(
            future[future["end_year"] > yr]["annual_cost"].sum()
            * _demand_multiplier(yr)
            for yr in years
        )
        / 1e9
    )

    scenarios = [
        ("flat", lambda yr: 1.0),
        ("growth", _demand_multiplier),
    ]

    builder = ChartBuilder(
        title="Existing CfD Obligations — contracts already signed (future rounds will add more)",
        height=900,
    )
    fig = builder.create_subplots(
        rows=2,
        cols=2,
        shared_xaxes=True,
        subplot_titles=[
            f"Annual — flat (£{total_flat_bn:.0f}bn total)",
            f"Annual — NESO growth (£{total_growth_bn:.0f}bn total)",
            "Cumulative — flat",
            "Cumulative — NESO growth",
        ],
        vertical_spacing=0.10,
        horizontal_spacing=0.08,
    )

    for col_idx, (scenario, multiplier_fn) in enumerate(scenarios, start=1):
        for ar, color in ROUND_COLORS.items():
            ar_units = future[future["Allocation_Round"] == ar]
            if ar_units.empty:
                continue

            annual_bn = []
            for yr in years:
                active = ar_units[ar_units["end_year"] > yr]
                annual_bn.append(active["annual_cost"].sum() * multiplier_fn(yr) / 1e9)

            cumulative_bn = list(np.cumsum(annual_bn))

            fig.add_trace(
                go.Bar(
                    x=years,
                    y=annual_bn,
                    name=ar,
                    marker_color=color,
                    showlegend=(col_idx == 1),
                    hovertemplate=f"{ar}<br>%{{x}}<br>£%{{y:.1f}}bn/yr<extra></extra>",
                ),
                row=1,
                col=col_idx,
            )

            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=cumulative_bn,
                    name=ar,
                    mode="lines",
                    line={"width": 0.5, "color": color},
                    stackgroup="cum",
                    fillcolor=color.replace(")", ",0.6)").replace("rgb", "rgba")
                    if "rgb" in color
                    else f"rgba({int(color[1:3], 16)},{int(color[3:5], 16)},{int(color[5:7], 16)},0.6)",
                    showlegend=False,
                    hovertemplate=f"{ar}<br>%{{x}}<br>£%{{y:.1f}}bn<extra></extra>",
                ),
                row=2,
                col=col_idx,
            )

    fig.update_layout(
        barmode="stack",
        hovermode="x unified",
    )
    for col in [1, 2]:
        fig.update_xaxes(title="Year", dtick=2, row=2, col=col)
        builder.format_currency_axis(
            fig,
            axis="y",
            suffix="bn",
            tickformat=".1f",
            title="£bn/yr" if col == 1 else "",
            row=1,
            col=col,
        )
        builder.format_currency_axis(
            fig,
            axis="y",
            suffix="bn",
            tickformat=".0f",
            title="Cumulative £bn" if col == 1 else "",
            row=2,
            col=col,
        )
        fig.update_yaxes(range=[0, 50], row=2, col=col)

    builder.save(fig, "subsidy_remaining_obligations", export_twitter=True)


if __name__ == "__main__":
    main()
