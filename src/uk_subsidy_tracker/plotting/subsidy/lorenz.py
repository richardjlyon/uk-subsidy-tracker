"""Lorenz curve — concentration of CfD subsidy by project.

Shows what fraction of total subsidy goes to what fraction of projects.
The further the curve bows from the diagonal, the more concentrated
the spending. The "equality line" (diagonal) represents every project
receiving the same amount.

Key finding: 6 projects receive 50% of all CfD subsidy. 11 projects
receive 80%. The "renewables revolution" is largely a handful of
Investment Contract offshore wind farms and Drax biomass.

Sources: LCCC "Actual CfD Generation and avoided GHG emissions".
Methodology:
- Total CfD levy payments (CFD_Payments_GBP) summed per unit over
  the full dataset lifetime.
- Only units with positive total payments included (units in net
  clawback excluded — they received no net subsidy).
- Projects sorted from largest to smallest recipient.
- X-axis = cumulative % of projects; Y-axis = cumulative % of £.
- Top recipients labelled by name.
"""

import numpy as np
import plotly.graph_objects as go

from uk_subsidy_tracker.data import load_lccc_dataset
from uk_subsidy_tracker.plotting import ChartBuilder


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")

    by_unit = (
        df.groupby(["Name_of_CfD_Unit", "Allocation_round"])
        .agg(payments=("CFD_Payments_GBP", "sum"))
        .reset_index()
    )
    by_unit = by_unit[by_unit["payments"] > 0].sort_values("payments", ascending=False)

    total = by_unit["payments"].sum()
    n = len(by_unit)
    cum_pct_payments = by_unit["payments"].cumsum() / total * 100
    cum_pct_projects = np.arange(1, n + 1) / n * 100

    total_bn = total / 1e9

    builder = ChartBuilder(
        title=f"CfD Subsidy Concentration — £{total_bn:.0f}bn across {n} projects, shared very unequally",
        height=650,
    )
    fig = builder.create_basic()

    # Equality line
    fig.add_trace(
        go.Scatter(
            x=[0, 100],
            y=[0, 100],
            mode="lines",
            line={"color": "grey", "width": 1, "dash": "dash"},
            name="Equal distribution",
            hoverinfo="skip",
        )
    )

    # Lorenz curve
    x_vals = [0] + cum_pct_projects.tolist()
    y_vals = [0] + cum_pct_payments.tolist()

    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            line={"color": "#d62728", "width": 3},
            name="Actual distribution",
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.1)",
            hoverinfo="skip",
        )
    )

    # Label key thresholds
    for threshold in [50, 80]:
        idx = (cum_pct_payments >= threshold).values.argmax()
        n_projects = idx + 1
        pct_projects = cum_pct_projects[idx]

        fig.add_trace(
            go.Scatter(
                x=[pct_projects],
                y=[threshold],
                mode="markers+text",
                marker={"size": 10, "color": "#d62728"},
                text=[f"{n_projects} projects = {threshold}% of £{total_bn:.0f}bn"],
                textposition="middle right",
                textfont={"size": 11},
                showlegend=False,
                hovertemplate=f"{n_projects} projects<br>{threshold}% of subsidy<extra></extra>",
            )
        )

    # Label top 3
    for i in range(min(3, n)):
        name = by_unit.iloc[i]["Name_of_CfD_Unit"]
        short = (
            name.replace(" Offshore Wind Farm", "")
            .replace("3rd conversion unit (unit 1)", "")
            .replace(" Power Station", "")
            .strip()
        )
        pmt = by_unit.iloc[i]["payments"] / 1e6
        fig.add_trace(
            go.Scatter(
                x=[cum_pct_projects[i]],
                y=[cum_pct_payments.iloc[i]],
                mode="markers+text",
                marker={"size": 8, "color": "#1f77b4"},
                text=[f"{short} (£{pmt:.0f}m)"],
                textposition="top left" if i > 0 else "bottom right",
                textfont={"size": 9},
                showlegend=False,
                hovertemplate=f"{name}<br>£{pmt:.0f}m<extra></extra>",
            )
        )

    fig.update_xaxes(
        title="Cumulative % of projects (largest first)",
        ticksuffix="%",
        range=[0, 100],
    )
    fig.update_yaxes(
        title="Cumulative % of total subsidy",
        ticksuffix="%",
        range=[0, 100],
    )
    fig.update_layout(showlegend=False)

    builder.save(fig, "subsidy_lorenz", export_twitter=True)


if __name__ == "__main__":
    main()
