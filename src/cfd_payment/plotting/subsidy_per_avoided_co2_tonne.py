"""Plot the subsidy per avoided CO2 tonne."""

import pandas as pd
import plotly.express as px

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df["Year"] = pd.to_datetime(df["Settlement_Date"]).dt.year

    grouped = (
        df.groupby(["Allocation_round", "Year"])
        .agg(
            payments=("CFD_Payments_GBP", "sum"),
            co2_avoided=("Avoided_GHG_tonnes_CO2e", "sum"),
        )
        .reset_index()
    )

    grouped["cost_per_tonne"] = grouped["payments"] / grouped["co2_avoided"]

    plot_data = grouped[
        (grouped["Year"].between(2017, 2025)) & (grouped["Year"] != 2022)
    ]

    fig = px.line(
        plot_data,
        x="Year",
        y="cost_per_tonne",
        color="Allocation_round",
        labels={
            "Year": "Year",
            "cost_per_tonne": "£ per tonne CO₂ avoided",
            "Allocation_round": "Allocation Round",
        },
        title="CfD Subsidy Cost per Tonne of CO₂ Avoided, by Allocation Round",
        markers=True,
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="£ per tonne CO₂ avoided",
        legend_title="Allocation Round",
    )

    fig.add_hline(
        y=280,
        line_dash="dash",
        line_color="red",
        annotation_text="DEFRA social cost of carbon (~£280/t)",
    )
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="grey",
        annotation_text="UK ETS price (~£50/t)",
    )

    save_chart(fig, "subsidy_per_avoided_co2_tonne")


if __name__ == "__main__":
    main()
