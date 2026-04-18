"""Monthly capacity factor by technology (time series).

One panel per technology via faceting — shows each technology's
seasonality clearly without overlapping lines.

Source: prepare_capacity_data() from capacity_factor/__init__.py.
Methodology: capacity-weighted fleet CF per (technology, month),
aggregated via aggregate_by_technology(). See __init__.py for
join and weighting details.
"""

import plotly.express as px

from cfd_payment.plotting import ChartBuilder
from cfd_payment.plotting.capacity_factor import (
    WIND_AND_SOLAR,
    aggregate_by_technology,
    prepare_capacity_data,
)


def main() -> None:
    merged = prepare_capacity_data(technologies=WIND_AND_SOLAR)
    by_tech = aggregate_by_technology(merged, groupby_cols=["month"])
    by_tech["month"] = by_tech["month"].dt.to_timestamp()

    builder = ChartBuilder(title="Monthly Capacity Factor by Technology", height=600)

    fig = px.line(
        by_tech,
        x="month",
        y="capacity_factor",
        color="Technology_Type",
        facet_col="Technology_Type",
        labels={
            "month": "",
            "capacity_factor": "Capacity Factor",
            "Technology_Type": "Technology",
        },
        markers=False,
    )

    # Apply ChartBuilder title with info icon
    title_with_icon = f"<b>{builder.title}</b>&nbsp;&nbsp;&nbsp;<span style='color:#00d9ff; border:2px solid #00d9ff; border-radius:50%; padding:2px 6px; font-size:16px;'>ⓘ</span>"
    fig.update_layout(
        title={
            "text": title_with_icon,
            "subtitle": {
                "text": "─" * 150,
                "font": {"size": 8, "color": "#4a5568"},
            },
            "x": 0.05,
            "xanchor": "left",
        },
        height=builder.height,
    )

    fig.update_yaxes(tickformat=".0%", title="Capacity Factor", matches="y")
    fig.update_xaxes(title="")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

    builder.save(fig, "capacity_factor_monthly", export_twitter=True)


if __name__ == "__main__":
    main()
