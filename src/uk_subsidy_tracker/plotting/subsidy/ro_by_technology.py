"""RO cost by technology — S3 stacked 2-panel.

Panels (CY x-axis per D-07):
  [1] Annual stacked bars by category (£bn per year).
  [2] Cumulative stacked area by category (£bn).

Categories (D-10 cofiring-vs-dedicated split; order matters — largest-lifetime
recipients declared first for consistent stack order across panels):

  Onshore Wind, Offshore Wind, Biomass (cofiring), Biomass (dedicated),
  Solar PV, Other.

Filename: ``subsidy_ro_by_technology`` per RO-MODULE-SPEC Appendix A.

Data source: ``data/derived/ro/by_technology.parquet`` (Plan 05-05). Robust
to empty upstream — emits a titled placeholder rather than raising so
``python -m uk_subsidy_tracker.plotting`` succeeds pre-Plan 05-13.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import ro

# Category ordering = stack order bottom-to-top (largest-lifetime first).
CATEGORIES: dict[str, str] = {
    "Offshore Wind": "#1f77b4",
    "Onshore Wind": "#6baed6",
    "Biomass (dedicated)": "#8c564b",
    "Biomass (cofiring)": "#d62728",
    "Solar PV": "#ff7f0e",
    "Other": "#2ca02c",
}

# Ofgem technology_type values → category buckets. Keys on the LHS are the
# raw Ofgem labels observed in the RO accreditation register; Plan 05-13
# post-execution review will reconcile these against the live register.
_TECH_MAP: dict[str, str] = {
    "Onshore wind": "Onshore Wind",
    "Onshore Wind": "Onshore Wind",
    "Offshore wind": "Offshore Wind",
    "Offshore Wind": "Offshore Wind",
    "Co-firing biomass": "Biomass (cofiring)",
    "Co-firing biomass (CHP)": "Biomass (cofiring)",
    "Co-firing energy crops": "Biomass (cofiring)",
    "Dedicated biomass": "Biomass (dedicated)",
    "Biomass Conversion": "Biomass (dedicated)",
    "Dedicated energy crops": "Biomass (dedicated)",
    "Solar PV — ground mounted": "Solar PV",
    "Solar PV — building mounted": "Solar PV",
    "Solar photovoltaic": "Solar PV",
    "Solar photovoltaic (pre-2013)": "Solar PV",
}


def _categorise(tech: str) -> str:
    return _TECH_MAP.get(tech, "Other")


def _prepare() -> pd.DataFrame:
    """Read by_technology.parquet and collapse to the 6 RO categories."""
    path = ro.DERIVED_DIR / "by_technology.parquet"
    if not path.exists():
        return pd.DataFrame()

    by_tech = pq.read_table(path).to_pandas()
    if len(by_tech) == 0:
        return by_tech

    by_tech["category"] = by_tech["technology"].map(_categorise)
    collapsed = (
        by_tech.groupby(["year", "category"], sort=True, observed=True)
        ["ro_cost_gbp"]
        .sum()
        .reset_index()
    )
    return collapsed


def _placeholder(builder: ChartBuilder) -> go.Figure:
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=(
            "<b>No RO data yet</b><br><br>"
            "data/derived/ro/by_technology.parquet is empty.<br>"
            "Regenerate after Ofgem RER URLs are plumbed (Plan 05-13)."
        ),
        showarrow=False,
        font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def main() -> None:
    df = _prepare()

    if len(df) == 0:
        builder = ChartBuilder(
            title="RO cost by technology (£bn per year, GB)",
            height=500,
        )
        fig = _placeholder(builder)
        builder.save(fig, "subsidy_ro_by_technology", export_twitter=True)
        return

    # Pivot wider for stacked plotting.
    pivot = (
        df.pivot_table(
            index="year",
            columns="category",
            values="ro_cost_gbp",
            aggfunc="sum",
            fill_value=0,
        )
        / 1e9  # £ → £bn
    )
    cum = pivot.cumsum()
    total_bn = float(cum.iloc[-1].sum()) if len(cum) else 0.0

    builder = ChartBuilder(
        title="RO cost by technology — where does the money go?",
        height=900,
    )
    fig = builder.create_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=[
            "[1] Annual £bn by category (GB)",
            f"[2] Cumulative — £{total_bn:.1f}bn total",
        ],
        vertical_spacing=0.08,
    )
    for ann in fig.layout.annotations[:2]:
        ann.update(xanchor="left", x=0.0)

    cat_order = list(CATEGORIES.keys())

    # Panel 1 — stacked bars by category.
    for cat in cat_order:
        if cat not in pivot.columns:
            continue
        fig.add_trace(
            go.Bar(
                x=pivot.index,
                y=pivot[cat],
                name=cat,
                marker_color=CATEGORIES[cat],
                hovertemplate=f"{cat}<br>%{{x}}<br>£%{{y:.2f}}bn<extra></extra>",
            ),
            row=1,
            col=1,
        )

    # Panel 2 — cumulative stack area (stackgroup='cum').
    for cat in cat_order:
        if cat not in cum.columns:
            continue
        hex_color = CATEGORIES[cat]
        r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
        fig.add_trace(
            go.Scatter(
                x=cum.index,
                y=cum[cat],
                name=cat,
                mode="lines",
                line={"width": 0.5, "color": hex_color},
                stackgroup="cum",
                fillcolor=f"rgba({r},{g},{b},0.6)",
                hovertemplate=f"{cat}<br>%{{x}}<br>£%{{y:.2f}}bn<extra></extra>",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    # D-10 footnote on cofiring attribution (adversarial-proofing).
    fig.add_annotation(
        text=(
            "Biomass split cofiring vs dedicated per D-10. "
            "GB-only; NI rows in Parquet via country='NI' filter."
        ),
        xref="paper",
        yref="paper",
        x=0.0,
        y=1.04,
        xanchor="left",
        yanchor="bottom",
        showarrow=False,
        font={"size": 9, "color": "#9ca3af"},
    )

    fig.update_layout(barmode="stack", hovermode="x unified")
    builder.format_currency_axis(
        fig, axis="y", suffix="bn", tickformat=".1f", title="£bn/yr", row=1, col=1
    )
    builder.format_currency_axis(
        fig, axis="y", suffix="bn", tickformat=".0f", title="Cumulative £bn", row=2, col=1
    )

    builder.save(fig, "subsidy_ro_by_technology", export_twitter=True)


if __name__ == "__main__":
    main()
