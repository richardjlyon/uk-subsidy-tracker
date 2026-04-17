"""Cumulative CfD payments over time, stacked by company."""

import plotly.express as px

from cfd_payment.data import load_lccc_dataset
from cfd_payment.plotting import save_chart


def main() -> None:
    df = load_lccc_dataset("Actual CfD Generation and avoided GHG emissions")
    df = df[df["Allocation_round"].isin(["Investment Contract", "Allocation Round 1"])]

    totals = (
        df.pivot_table(
            index="Settlement_Date",
            columns="Name_of_CfD_Unit",
            values="CFD_Payments_GBP",
            aggfunc="sum",
            fill_value=0,
        )
        .sort_index()
        .cumsum()
    )

    totals = totals / 1e9

    cum = totals.stack().rename("Cumulative_CFD_Payments_GBP").reset_index()

    fig = px.area(
        cum,
        x="Settlement_Date",
        y="Cumulative_CFD_Payments_GBP",
        color="Name_of_CfD_Unit",
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Cumulative CFD Payments (GBP)",
        legend_title="Company",
        title_text="Cumulative CfD Payments by Company (IC and AR1 only)",
    )

    save_chart(fig, "cumulative_payments_by_company")


if __name__ == "__main__":
    main()
