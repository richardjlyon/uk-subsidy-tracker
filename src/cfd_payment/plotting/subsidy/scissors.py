"""Guaranteed price vs market price — the CfD scissors chart.

Two-panel chart with shared x-axis:
- Top: three price lines in £/MWh — what we pay generators (guaranteed
  price), what the electricity is worth (market price), and what gas
  would cost (fuel only). The gap between blue and red = subsidy per MWh.
- Bottom: monthly CfD levy payments in £m — the total cost consequence
  of the per-MWh gap above, scaled by generation volume.

Sources: LCCC "Actual CfD Generation", ONS gas price data.
Methodology:
- Guaranteed price = generation-weighted average strike price across
  all CfD units per month.
- Market price = generation-weighted average market reference price.
- Gas fuel cost = ONS daily SAP via 55% CCGT efficiency, no carbon,
  averaged monthly.
- CfD payments = sum(CFD_Payments_GBP) per month — the actual levy
  cost to consumers (= (strike - market) × generation).
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment.counterfactual import compute_counterfactual_monthly
from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart


def _weighted_monthly(df: pd.DataFrame, col: str) -> pd.Series:
    df = df.dropna(subset=[col, "CFD_Generation_MWh"])
    df = df[df["CFD_Generation_MWh"] > 0]

    def _wavg(g):
        if g["CFD_Generation_MWh"].sum() <= 0:
            return np.nan
        return np.average(g[col], weights=g["CFD_Generation_MWh"])

    return df.groupby("month").apply(_wavg)


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df["month"] = df["Settlement_Date"].dt.to_period("M").dt.to_timestamp()

    fleet_strike = _weighted_monthly(df, "Strike_Price_GBP_Per_MWh")
    fleet_mrp = _weighted_monthly(df, "Market_Reference_Price_GBP_Per_MWh")

    cf = compute_counterfactual_monthly(carbon_prices={})
    cf.index = cf["date"].dt.to_period("M").dt.to_timestamp()

    monthly_payments = (
        df.groupby("month")["CFD_Payments_GBP"].sum() / 1e6
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Price per MWh — the gap is the subsidy",
            "Monthly CfD levy payments — what the gap costs consumers",
        ],
        vertical_spacing=0.08,
    )

    # --- Top panel: price lines ---
    fig.add_trace(
        go.Scatter(
            x=fleet_strike.index,
            y=fleet_strike.values,
            name="What we pay generators (guaranteed price)",
            mode="lines",
            line={"color": "#1f77b4", "width": 3},
            hovertemplate="Guaranteed price<br>%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=fleet_mrp.index,
            y=fleet_mrp.values,
            name="What the electricity is worth (market price)",
            mode="lines",
            line={"color": "#d62728", "width": 3},
            hovertemplate="Market price<br>%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=cf.index,
            y=cf["gas_fuel_cost"],
            name="What gas would cost (fuel only, no carbon tax)",
            mode="lines",
            line={"color": "#ff7f0e", "width": 2.5},
            hovertemplate="Gas fuel cost<br>%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
        ),
        row=1,
        col=1,
    )

    # Shade the gap between guaranteed and market price
    common_idx = fleet_strike.dropna().index.intersection(fleet_mrp.dropna().index)
    fig.add_trace(
        go.Scatter(
            x=common_idx.tolist() + common_idx.tolist()[::-1],
            y=fleet_strike.reindex(common_idx).tolist()
            + fleet_mrp.reindex(common_idx).tolist()[::-1],
            fill="toself",
            fillcolor="rgba(31,119,180,0.1)",
            line={"width": 0},
            showlegend=False,
            hoverinfo="skip",
        ),
        row=1,
        col=1,
    )

    # --- Bottom panel: monthly CfD payments ---
    bar_colors = [
        "#1f77b4" if v >= 0 else "#2ca02c" for v in monthly_payments.values
    ]

    fig.add_trace(
        go.Bar(
            x=monthly_payments.index,
            y=monthly_payments.values,
            name="CfD levy payment (green = clawback)",
            marker_color=bar_colors,
            hovertemplate="%{x|%b %Y}<br>£%{y:.0f}m<extra></extra>",
        ),
        row=2,
        col=1,
    )

    fig.update_yaxes(
        title="£/MWh",
        tickprefix="£",
        ticksuffix="/MWh",
        rangemode="tozero",
        row=1,
        col=1,
    )
    fig.update_yaxes(
        title="£ millions",
        tickprefix="£",
        ticksuffix=" m",
        tickformat="~g",
        row=2,
        col=1,
    )
    fig.update_layout(
        title="What we pay CfD generators vs what the electricity is worth",
        height=900,
        hovermode="x unified",
        bargap=0,
    )

    save_chart(fig, "subsidy_scissors")


if __name__ == "__main__":
    main()
