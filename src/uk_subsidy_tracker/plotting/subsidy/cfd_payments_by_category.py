"""CfD payments by technology category — monthly and cumulative.

Two-panel chart with shared x-axis:
- Top: monthly CfD electricity cost stacked by technology category.
  Shows where the money goes each month.
- Bottom: cumulative stacked area of the same — shows how total spend
  accumulates and which technologies dominate the lifetime cost.

Sources: LCCC "Actual CfD Generation and avoided GHG emissions".
Methodology:
- CfD cost per row = (reference_price × generation) + CFD_Payments_GBP,
  summed per category per month. Matches the cost basis used in
  cfd_vs_gas_cost.py so cumulative totals reconcile exactly (wholesale
  paid on the bill + CfD levy top-up paid via the Supplier Obligation).
- Using CFD_Payments_GBP directly (rather than strike × gen − reference × gen)
  picks up LCCC settlement adjustments — negative-pricing suspensions,
  cap/floor rules, settlement re-runs — so the totals here match cash
  actually transferred.
- Categories: Offshore Wind, Onshore Wind, Biomass Conversion, Other.
  Wind split into onshore/offshore to reveal which drives the cost.
- No gas counterfactual here — that comparison is in cfd_vs_gas_cost.py.
  This chart is purely "where does the CfD money go?"
"""

import plotly.graph_objects as go

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import ChartBuilder

CATEGORIES = {
    "Offshore Wind": "#1f77b4",
    "Onshore Wind": "#6baed6",
    "Biomass (Drax & Lynemouth)": "#d62728",
    "Other": "#2ca02c",
}

_TECH_MAP = {
    "Offshore Wind": "Offshore Wind",
    "Onshore Wind": "Onshore Wind",
    "Biomass Conversion": "Biomass (Drax & Lynemouth)",
}


def _categorise(tech: str) -> str:
    return _TECH_MAP.get(tech, "Other")


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")

    df["category"] = df["Technology"].map(_categorise)
    df["month"] = df["Settlement_Date"].dt.to_period("M").dt.to_timestamp()
    df["cfd_cost"] = (
        df["Market_Reference_Price_GBP_Per_MWh"] * df["CFD_Generation_MWh"]
        + df["CFD_Payments_GBP"]
    )

    pivot_m = (
        df.pivot_table(
            index="month",
            columns="category",
            values="cfd_cost",
            aggfunc="sum",
            fill_value=0,
        )
        / 1e6
    )

    cum_bn = pivot_m.cumsum() / 1e3
    total_bn = cum_bn.iloc[-1].sum()

    builder = ChartBuilder(
        title="CfD Payments by Technology — where does the money go?",
        height=900,
    )
    fig = builder.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "Monthly CfD cost by technology",
            f"Cumulative — £{total_bn:.0f}bn total",
        ],
        vertical_spacing=0.08,
    )

    cat_order = list(CATEGORIES.keys())

    for cat in cat_order:
        if cat not in pivot_m.columns:
            continue
        fig.add_trace(
            go.Bar(
                x=pivot_m.index,
                y=pivot_m[cat],
                name=cat,
                marker_color=CATEGORIES[cat],
                hovertemplate=f"{cat}<br>%{{x|%b %Y}}<br>£%{{y:.0f}}m<extra></extra>",
            ),
            row=1,
            col=1,
        )

    for cat in cat_order:
        if cat not in cum_bn.columns:
            continue
        fig.add_trace(
            go.Scatter(
                x=cum_bn.index,
                y=cum_bn[cat],
                name=cat,
                mode="lines",
                line={"width": 0.5, "color": CATEGORIES[cat]},
                stackgroup="cumulative",
                fillcolor=CATEGORIES[cat].replace(")", ",0.6)").replace("rgb", "rgba")
                if "rgb" in CATEGORIES[cat]
                else f"rgba({int(CATEGORIES[cat][1:3], 16)},{int(CATEGORIES[cat][3:5], 16)},{int(CATEGORIES[cat][5:7], 16)},0.6)",
                hovertemplate=f"{cat}<br>%{{x|%b %Y}}<br>£%{{y:.1f}}bn<extra></extra>",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    fig.update_layout(
        barmode="relative",
        hovermode="x unified",
    )

    builder.format_currency_axis(
        fig,
        axis="y",
        suffix="m",
        title="£ millions",
        row=1,
        col=1,
    )
    builder.format_currency_axis(
        fig,
        axis="y",
        suffix="bn",
        title="£ billions",
        row=2,
        col=1,
    )

    builder.save(fig, "subsidy_cfd_payments_by_category", export_twitter=True)


if __name__ == "__main__":
    main()
