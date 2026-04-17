"""Monthly CfD payments vs market price vs gas-only counterfactual."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from cfd_payment.counterfactual import compute_counterfactual_monthly
from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import format_gbp_axis, make_dual_axis_figure, save_chart

FREQ = "ME"


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")

    payments = (
        df.groupby(pd.Grouper(key="Settlement_Date", freq=FREQ))[
            "CFD_Payments_GBP"
        ].sum()
        / 1e6
    )

    valid = df.dropna(
        subset=["Market_Reference_Price_GBP_Per_MWh", "CFD_Generation_MWh"]
    )
    grouped = valid.groupby(pd.Grouper(key="Settlement_Date", freq=FREQ))
    weighted_mrp = grouped.apply(
        lambda g: (
            np.average(
                g["Market_Reference_Price_GBP_Per_MWh"],
                weights=g["CFD_Generation_MWh"],
            )
            if g["CFD_Generation_MWh"].sum() > 0
            else np.nan
        )
    )

    cf = compute_counterfactual_monthly(carbon_prices={})
    cf = cf.set_index("date")["gas_fuel_cost"]

    fig = make_dual_axis_figure()

    fig.add_trace(
        go.Bar(
            x=payments.index,
            y=payments.values,
            name="CfD payments",
            marker_color="#1f77b4",
            opacity=0.7,
            hovertemplate="%{x|%b %Y}<br>£%{y:.0f}m<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=weighted_mrp.index,
            y=weighted_mrp.values,
            name="Market reference price (gen-weighted)",
            mode="lines+markers",
            line={"color": "#d62728", "width": 2},
            marker={"size": 4},
            hovertemplate="%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(
            x=cf.index,
            y=cf.values,
            name="Counterfactual gas-only price (no carbon)",
            mode="lines",
            line={"color": "#ff7f0e", "width": 2, "dash": "dash"},
            hovertemplate="%{x|%b %Y}<br>£%{y:.0f}/MWh<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=(
            "Monthly CfD Payments vs Market Price vs Gas-Only Counterfactual — "
            "the pure fuel cost of generating from gas, excluding carbon tax"
        ),
        hovermode="x unified",
        bargap=0.1,
    )
    fig.update_xaxes(title="Settlement Date")
    format_gbp_axis(fig, suffix=" m", title="CfD payments (£ millions)")
    format_gbp_axis(
        fig, suffix="/MWh", title="Electricity price (£/MWh)", secondary_y=True
    )

    save_chart(fig, "payments_vs_gas_price")


if __name__ == "__main__":
    main()
