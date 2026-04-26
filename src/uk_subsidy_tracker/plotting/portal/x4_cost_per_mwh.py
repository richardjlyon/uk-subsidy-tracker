"""X4 — Cost per MWh of subsidised generation by scheme.

Time series, one line per scheme. NaN-generation rows are dropped (pre-SY18 RO
years per cross_scheme schema D-02). Schemes without a gas counterfactual
(CM, Balancing, Grid) are excluded — listed in :data:`EXCLUDED_SCHEMES`; the
filter is no-op in Phase 6 (those schemes don't yet exist in
``cross_scheme.parquet``) but armed for Phase 9-11. REQUIREMENT X-04. D-16
footnote in chart subtitle.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import pyarrow.parquet as pq

from uk_subsidy_tracker.plotting import ChartBuilder
from uk_subsidy_tracker.plotting.colors import SCHEME_COLORS
from uk_subsidy_tracker.schemes import portal

# D-16: schemes without gas counterfactual are excluded from X4 + X5.
# No-op in Phase 6 (these schemes ship in Phases 9-11); armed for the future.
EXCLUDED_SCHEMES: frozenset[str] = frozenset({
    "Capacity Market",
    "Balancing Services",
    "Grid Socialisation",
})


def _prepare() -> pd.DataFrame:
    """Read cross_scheme.parquet, exclude no-counterfactual schemes, drop NaN-gen rows.

    Returns the long-format frame with a ``cost_per_mwh`` column. Empty
    DataFrame returned when the parquet is absent or zero-row, so ``main()``
    can short-circuit to the placeholder figure.
    """
    src = portal.DERIVED_DIR / "cross_scheme.parquet"
    if not src.exists():
        return pd.DataFrame()
    df = pq.read_table(src).to_pandas()
    if len(df) == 0:
        return df
    # D-16: omit no-gas-counterfactual schemes (no-op in Phase 6).
    df = df[~df["scheme"].isin(EXCLUDED_SCHEMES)]
    # Drop NaN-generation rows (pre-SY18 RO; HAZARD #2 from cross_scheme schema).
    df = df[df["generation_mwh"].notna() & (df["generation_mwh"] > 0)].copy()
    df["cost_per_mwh"] = df["cost_gbp"] / df["generation_mwh"]
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
            "<b>No cross-scheme cost-per-MWh data yet</b><br><br>"
            "data/derived/portal/cross_scheme.parquet is empty or "
            "lacks generation MWh."
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
        title="Cost per MWh of subsidised generation by scheme",
        height=600,
    )
    if df.empty:
        fig = _placeholder(builder)
        builder.save(fig, "x4_cost_per_mwh", export_twitter=True)
        return

    fig = builder.create_basic()
    for scheme_name, sub in df.groupby("scheme", sort=False):
        fig.add_trace(
            go.Scatter(
                x=sub["year"],
                y=sub["cost_per_mwh"],
                name=str(scheme_name),
                mode="lines+markers",
                line={"color": SCHEME_COLORS[str(scheme_name)], "width": 2.5},
                marker={"size": 7},
                hovertemplate=(
                    "%{x}<br>"
                    + str(scheme_name)
                    + "<br>£%{y:,.0f}/MWh<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title=dict(
            text="<b>Cost per MWh of subsidised generation by scheme</b>",
            subtitle=dict(
                text="Schemes without a gas counterfactual (CM, Balancing, Grid) excluded — see methodology.",
                font=dict(size=12, color="#a0a4b8"),
            ),
            x=0.05,
            xanchor="left",
        ),
    )
    fig.update_xaxes(title="Year")
    builder.format_currency_axis(fig, axis="y", title="Cost per MWh (£/MWh)")
    builder.save(
        fig,
        "x4_cost_per_mwh",
        export_twitter=True,
        export_html=True,
        export_div=True,
    )


if __name__ == "__main__":
    main()
