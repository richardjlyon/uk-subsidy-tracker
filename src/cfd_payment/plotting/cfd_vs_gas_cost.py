"""
CfD cost vs gas counterfactual — what did we pay for CfD electricity
vs what the same MWh would have cost from gas?
"""

import plotly.graph_objects as go

from cfd_payment.counterfactual import compute_counterfactual_monthly
from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart


def _categorise(tech: str) -> str:
    if "Wind" in tech:
        return "Wind"
    if tech == "Biomass Conversion":
        return "Drax (Biomass Conversion)"
    return "Other"


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    cf = compute_counterfactual_monthly(carbon_prices={})
    cf.index = cf["date"].dt.to_period("M").dt.to_timestamp()
    cf = cf[["gas_fuel_cost"]]

    df["category"] = df["Technology"].map(_categorise)
    df["month"] = df["Settlement_Date"].dt.to_period("M").dt.to_timestamp()

    monthly_gen = df.groupby("month")["CFD_Generation_MWh"].sum()

    gas_cost = (
        cf["gas_fuel_cost"].reindex(monthly_gen.index).multiply(monthly_gen).dropna()
    )

    df["strike_times_gen"] = df["Strike_Price_GBP_Per_MWh"] * df["CFD_Generation_MWh"]

    cat_strike = (
        df.groupby(["month", "category"])["strike_times_gen"].sum().reset_index()
    )
    cat_gen = (
        df.groupby(["month", "category"])["CFD_Generation_MWh"].sum().reset_index()
    )

    merged = cat_strike.merge(cat_gen, on=["month", "category"])
    merged = merged.merge(
        cf["gas_fuel_cost"].rename("gas_price"),
        left_on="month",
        right_index=True,
    )
    merged["gas_cost"] = merged["gas_price"] * merged["CFD_Generation_MWh"]
    merged["premium"] = merged["strike_times_gen"] - merged["gas_cost"]
    merged["premium_m"] = merged["premium"] / 1e6

    pivot = merged.pivot_table(
        index="month", columns="category", values="premium_m", fill_value=0
    )

    gas_cost_m = gas_cost / 1e6

    cat_order = ["Drax (Biomass Conversion)", "Wind", "Other"]
    cat_colors = {
        "Drax (Biomass Conversion)": "#d62728",
        "Wind": "#1f77b4",
        "Other": "#2ca02c",
    }

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=gas_cost_m.index,
            y=gas_cost_m.values,
            name="Gas fuel cost (counterfactual)",
            marker_color="#ff7f0e",
            hovertemplate="%{x|%b %Y}<br>£%{y:.0f}m<extra></extra>",
        )
    )

    for cat in cat_order:
        if cat in pivot.columns:
            fig.add_trace(
                go.Bar(
                    x=pivot.index,
                    y=pivot[cat].values,
                    name=f"CfD premium: {cat}",
                    marker_color=cat_colors[cat],
                    hovertemplate="%{x|%b %Y}<br>£%{y:.0f}m<extra></extra>",
                )
            )

    fig.update_layout(
        barmode="relative",
        title=(
            "What CfD electricity cost vs what the same MWh would cost from gas — "
            "gas fuel cost + CfD premium by category"
        ),
        hovermode="x unified",
        bargap=0.1,
    )
    fig.update_xaxes(title="Month")
    fig.update_yaxes(
        title_text="Total cost (£ millions)",
        tickprefix="£",
        ticksuffix=" m",
        tickformat="~g",
    )

    save_chart(fig, "cfd_vs_gas_cost")


if __name__ == "__main__":
    main()
