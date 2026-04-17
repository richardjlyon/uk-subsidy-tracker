"""Cumulative CfD payments over time, stacked by technology."""

import plotly.express as px

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import format_gbp_axis, save_chart, technology_color_map


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")

    totals = (
        df.pivot_table(
            index="Settlement_Date",
            columns="Technology",
            values="CFD_Payments_GBP",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
        .cumsum()
    )

    totals = totals / 1e9

    tech_order = totals.iloc[-1].sort_values(ascending=False).index.tolist()
    color_map = technology_color_map(list(totals.columns))

    cum = totals.stack().rename("Cumulative_CFD_Payments_GBP").reset_index()

    fig = px.area(
        cum,
        x="Settlement_Date",
        y="Cumulative_CFD_Payments_GBP",
        color="Technology",
        category_orders={"Technology": tech_order},
        color_discrete_map=color_map,
        labels={
            "Settlement_Date": "Settlement Date",
            "Cumulative_CFD_Payments_GBP": "Cumulative CfD Payments (£ billions)",
        },
        title="Cumulative CfD Payments Over Time, by Technology",
    )

    format_gbp_axis(fig, suffix=" bn", title="Cumulative CfD Payments (£ billions)")

    save_chart(fig, "cumulative_payments")


if __name__ == "__main__":
    main()
