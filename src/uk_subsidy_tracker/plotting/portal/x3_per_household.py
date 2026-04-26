"""X3 — Cost per UK household, decomposed by scheme.

PORTAL-01 P1 flagship chart. Per-household division uses ONS UK
households-count carried per-row in ``cross_scheme.parquet`` (D-02). Pre-2014
bars omitted because ``households_uk`` is null pre-ONS-Families-and-Households-
series start (RESEARCH Q3 recommendation); the methodology page documents.

REQUIREMENT X-03.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.plotting.colors import SCHEME_COLORS
from uk_subsidy_tracker.schemes import portal


def _prepare() -> pd.DataFrame:
    """Read cross_scheme.parquet, drop pre-2014 rows, compute per-household cost.

    Empty DataFrame on absent/zero-row substrate. Rows with NaN or non-positive
    ``households_uk`` are dropped (pre-2014 RO years; RESEARCH Q3) — the
    methodology page documents the omission for hostile readers.
    """
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    if len(df) == 0:
        return df
    # Drop rows with missing households_uk (pre-2014; RESEARCH Q3 recommendation
    # — methodology.md documents the omission).
    df = df[df["households_uk"].notna() & (df["households_uk"] > 0)].copy()
    df["per_household_gbp"] = df["cost_gbp"] / df["households_uk"]
    return df


def _placeholder(builder: ChartBuilder) -> go.Figure:
    """Titled single-panel placeholder for the empty-substrate path."""
    fig = builder.create_basic()
    fig.add_annotation(
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        text=(
            "<b>No per-household data yet</b><br><br>"
            "data/derived/portal/cross_scheme.parquet is empty<br>"
            "(or has no rows with non-null households_uk).<br>"
            "Run schemes.portal.rebuild_derived() first."
        ),
        showarrow=False,
        font={"size": 14, "color": "#9ca3af"},
    )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def main() -> None:
    df = _prepare()
    builder = ChartBuilder(
        title="Cost per UK household by scheme",
        height=600,
    )
    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x3_per_household", export_twitter=True)
        return

    fig = builder.create_basic()
    for scheme_name, sub in df.groupby("scheme", sort=False):
        fig.add_trace(
            go.Bar(
                x=sub["year"],
                y=sub["per_household_gbp"],
                name=str(scheme_name),
                marker_color=SCHEME_COLORS[str(scheme_name)],
                hovertemplate=(
                    "%{x}<br>"
                    + str(scheme_name)
                    + "<br>£%{y:,.0f}/household<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="stack",
        title=dict(
            text="<b>Cost per UK household by scheme</b>",
            subtitle=dict(
                text="Covers 2 of 8 schemes; ONS UK households-count denominator — see methodology.",
                font=dict(size=12, color="#a0a4b8"),
            ),
            x=0.05,
            xanchor="left",
        ),
    )
    fig.update_xaxes(title="Year")
    builder.format_currency_axis(fig, axis="y", title="Cost per household (£)")
    builder.save(
        fig,
        "x3_per_household",
        export_twitter=True,
        export_html=True,
        export_div=True,
    )


if __name__ == "__main__":
    main()
