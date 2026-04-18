"""Average capacity factor by calendar month (Jan-Dec).

Collapses all years into a single seasonal profile per technology.
Individual years shown in faint gray to convey inter-annual variability.
DESNZ planning assumptions shown as horizontal reference lines.

Source: prepare_capacity_data() from capacity_factor/__init__.py.
Methodology: capacity-weighted fleet CF aggregated by calendar month
(1-12) across all years. Per-year traces use the same weighting.
DESNZ reference lines are planning assumptions for new CfD projects
(2027-2031): offshore 49%, onshore 36%, solar 11%.
Caveat: CfD actual average is the mean of monthly CFs, not a true
capacity-weighted annual figure — the difference is negligible since
months are roughly equal length.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from cfd_payment.plotting import ChartBuilder
from cfd_payment.plotting.capacity_factor import (
    WIND_AND_SOLAR,
    aggregate_by_technology,
    prepare_capacity_data,
)

MONTH_NAMES = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

DESNZ_ASSUMPTIONS = {
    "Offshore Wind": 0.49,
    "Onshore Wind": 0.36,
    "Solar PV": 0.11,
}

TECH_COLORS = {
    "Offshore Wind": "#1f77b4",
    "Onshore Wind": "#d62728",
    "Solar PV": "#2ca02c",
}


def main() -> None:
    merged = prepare_capacity_data(technologies=WIND_AND_SOLAR)
    merged["calendar_month"] = merged["month"].dt.month
    merged["year"] = merged["month"].dt.year

    avg = aggregate_by_technology(merged, groupby_cols=["calendar_month"])
    avg["month_name"] = avg["calendar_month"].map(lambda m: MONTH_NAMES[m - 1])

    by_year = aggregate_by_technology(merged, groupby_cols=["calendar_month", "year"])
    by_year["month_name"] = by_year["calendar_month"].map(lambda m: MONTH_NAMES[m - 1])

    techs = WIND_AND_SOLAR

    builder = ChartBuilder(
        title="Seasonal Capacity Factor by Technology — Average (bold) vs Individual Years (gray)",
        height=700,
    )

    fig = builder.create_subplots(
        rows=1,
        cols=len(techs),
        shared_yaxes=True,
        subplot_titles=techs,
    )

    for col_idx, tech in enumerate(techs, start=1):
        tech_years = by_year[by_year["Technology_Type"] == tech]
        for year in sorted(tech_years["year"].unique()):
            year_data = tech_years[tech_years["year"] == year].sort_values(
                "calendar_month"
            )
            fig.add_trace(
                go.Scatter(
                    x=year_data["month_name"],
                    y=year_data["capacity_factor"],
                    mode="lines",
                    line={"color": "rgba(120,120,120,0.5)", "width": 1},
                    showlegend=False,
                    hovertemplate=f"{year}<br>%{{x}}: %{{y:.0%}}<extra></extra>",
                ),
                row=1,
                col=col_idx,
            )

        tech_avg = avg[avg["Technology_Type"] == tech].sort_values("calendar_month")
        fig.add_trace(
            go.Scatter(
                x=tech_avg["month_name"],
                y=tech_avg["capacity_factor"],
                mode="lines+markers",
                line={"color": TECH_COLORS[tech], "width": 3},
                marker={"size": 6},
                name=f"{tech} (avg)",
                hovertemplate="%{x}: %{y:.1%}<extra></extra>",
            ),
            row=1,
            col=col_idx,
        )

        annual_avg = tech_avg["capacity_factor"].mean()
        fig.add_hline(
            y=annual_avg,
            line_dash="dot",
            line_color=TECH_COLORS[tech],
            line_width=1.5,
            annotation_text=f"CfD actual avg ({annual_avg:.0%})",
            annotation_position="top right",
            annotation_font_size=10,
            row=1,
            col=col_idx,
        )

        assumption = DESNZ_ASSUMPTIONS.get(tech)
        if assumption:
            fig.add_hline(
                y=assumption,
                line_dash="dash",
                line_color="black",
                line_width=1.5,
                annotation_text=f"DESNZ assumption ({assumption:.0%})",
                annotation_position="bottom right",
                annotation_font_size=10,
                row=1,
                col=col_idx,
            )

    fig.update_yaxes(tickformat=".0%", title="Capacity Factor", col=1)
    fig.update_yaxes(tickformat=".0%", col=2)
    fig.update_yaxes(tickformat=".0%", col=3)
    fig.update_xaxes(
        categoryorder="array",
        categoryarray=MONTH_NAMES,
    )
    fig.update_layout(
        showlegend=False,
    )

    builder.save(fig, "capacity_factor_seasonal", export_twitter=True)


if __name__ == "__main__":
    main()
