"""X2 — Cumulative premium over gas, combined across covered schemes.

PORTAL-01 P1 flagship chart. REQUIREMENT X-02.

Single-figure layout (no rangeselector). Sums ``premium_gbp`` across schemes
per year, then takes the cumulative sum. D-08 conformance: only shipped-scheme
rows live in ``cross_scheme.parquet``, so the combined sum naturally reflects
the partial-coverage caveat — the subtitle is explicit about that.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.schemes import portal


def _prepare() -> pd.DataFrame:
    """Read cross_scheme.parquet. Empty DataFrame on absent/zero-row substrate.

    No categorical-sort step (X2 sums across schemes per year — there is no
    stack to order).
    """
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    if len(df) == 0:
        return df
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
            "<b>No cross-scheme premium data yet</b><br><br>"
            "data/derived/portal/cross_scheme.parquet is empty.<br>"
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
        title="Cumulative premium over gas — covered schemes",
        height=600,
    )
    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x2_cumulative_premium", export_twitter=True)
        return

    # Sum premium across schemes per year, then cumulative sum.
    # D-08 conformance: only shipped-scheme rows present in cross_scheme.parquet,
    # so the combined sum naturally reflects the partial-coverage caveat.
    combined = (
        df.groupby("year")["premium_gbp"].sum().sort_index().cumsum() / 1e9
    )
    fig = builder.create_basic()
    fig.add_trace(
        go.Scatter(
            x=pd.to_datetime(combined.index, format="%Y"),
            y=combined.values,
            mode="lines+markers",
            line={"color": "#d62728", "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(214,39,40,0.25)",
            hovertemplate="%{x|%Y}<br>£%{y:.1f}bn<extra></extra>",
            name="Cumulative premium",
        )
    )
    fig.update_layout(
        title=dict(
            text="<b>Cumulative premium over gas — covered schemes</b>",
            subtitle=dict(
                text="Covers 2 of 8 schemes — see scheme grid for coverage status.",
                font=dict(size=12, color="#a0a4b8"),
            ),
            x=0.05,
            xanchor="left",
        ),
        showlegend=False,
    )
    fig.update_xaxes(type="date", title="Year")
    builder.format_currency_axis(
        fig, axis="y", suffix=" bn", title="Cumulative premium (£bn)"
    )
    builder.save(
        fig,
        "x2_cumulative_premium",
        export_twitter=True,
        export_html=True,
        export_div=True,
    )


if __name__ == "__main__":
    main()
